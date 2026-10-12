import asyncio
import re
from collections import Counter
from pathlib import Path

from pydantic import BaseModel

from app.config.settings import get_settings
from app.core.exceptions import LLMOutputError
from app.schemas.support import EmailCategory, SupportReply, Urgency
from app.services.llm_client import LLMClient
from app.services.support_service import SupportService

CASES_PATH = Path(__file__).parent / "support_cases.jsonl"
REPEATS = 3
MAX_CONCURRENCY = 2
MAX_RETRIES = 10
MAX_REPLY_WORDS = 150
SIGN_OFF = "The Support Team"
ARABIC = re.compile(r"[؀-ۿ]")
MARKDOWN = re.compile(r"\*\*|^#+ |^\s*[-*] ", re.MULTILINE)


class EvalCase(BaseModel):
    id: str
    text: str
    category: EmailCategory
    urgency: Urgency | None = None
    language: str = "en"
    forbidden: list[str] = []


def load_cases() -> list[EvalCase]:
    lines = CASES_PATH.read_text(encoding="utf-8").splitlines()
    return [EvalCase.model_validate_json(line) for line in lines if line.strip()]


async def predict(service: SupportService, case: EvalCase) -> SupportReply | None:
    try:
        return await service.reply(case.text)
    except LLMOutputError as error:
        print(f"[{case.id}] error: {error}")
        return None


def score(case: EvalCase, result: SupportReply) -> dict[str, bool]:
    reply = result.reply
    lowered = reply.casefold()
    scores = {
        "category": result.classification.category == case.category,
        "same_language": bool(ARABIC.search(reply)) == (case.language == "ar"),
        "no_markdown": not MARKDOWN.search(reply),
        "short": len(reply.split()) <= MAX_REPLY_WORDS,
        "no_forbidden": not any(p.casefold() in lowered for p in case.forbidden),
    }
    if case.urgency is not None:
        scores["urgency"] = result.classification.urgency == case.urgency
    if case.language == "en":
        scores["signed_off"] = SIGN_OFF.casefold() in lowered
    return scores


def describe(check: str, result: SupportReply) -> str:
    if check in ("category", "urgency"):
        return str(getattr(result.classification, check))
    return result.reply[:100].replace("\n", " ")


async def main() -> None:
    cases = load_cases()
    settings = get_settings().model_copy(update={"llm_max_retries": MAX_RETRIES})
    client = LLMClient(settings)
    service = SupportService(client)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def run(case: EvalCase) -> tuple[EvalCase, SupportReply | None]:
        async with semaphore:
            return case, await predict(service, case)

    try:
        results = await asyncio.gather(
            *(run(case) for case in cases for _ in range(REPEATS))
        )
    finally:
        await client.close()

    passed: Counter[str] = Counter()
    totals: Counter[str] = Counter()
    errors = 0
    for case, result in results:
        if result is None:
            errors += 1
            continue
        for check, ok in score(case, result).items():
            totals[check] += 1
            passed[check] += ok
            if not ok:
                print(f"[{case.id}] {check} failed: {describe(check, result)}")

    print(f"\n{len(cases)} cases x {REPEATS} runs, {errors} errors")
    for check, total in totals.items():
        print(f"{check:<14} {passed[check]}/{total}  {passed[check] / total:.0%}")


if __name__ == "__main__":
    asyncio.run(main())
