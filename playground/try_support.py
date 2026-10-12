import asyncio

from app.config.settings import get_settings
from app.core.logger import setup_logging
from app.services.llm_client import LLMClient
from app.services.support_service import SupportService

EMAIL = """\
Hi, I was charged twice for my Pro plan this month (invoice INV-2291).
I'm on a tight budget, please fix this asap.
Thanks, Sara
"""


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    llm_client = LLMClient(settings)
    try:
        result = await SupportService(llm_client).reply(EMAIL)
        print(result.model_dump_json(indent=2))
    finally:
        await llm_client.close()


asyncio.run(main())
