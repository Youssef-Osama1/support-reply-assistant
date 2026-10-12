import logging

from app.core.exceptions import LLMOutputError
from app.prompts.support import (
    CLASSIFICATION_SYSTEM_PROMPT,
    build_email_prompt,
    build_reply_prompt,
    build_reply_system_prompt,
)
from app.schemas.support import EmailClassification, SupportReply
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SupportService:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def reply(self, email_text: str) -> SupportReply:
        classification = await self.classify(email_text)
        reply = await self._llm_client.complete(
            prompt=build_reply_prompt(email_text, classification),
            system=build_reply_system_prompt(classification.category),
        )
        if not reply.strip():
            raise LLMOutputError("Model returned an empty reply")
        return SupportReply(classification=classification, reply=reply.strip())

    async def classify(self, email_text: str) -> EmailClassification:
        classification = await self._llm_client.extract(
            prompt=build_email_prompt(email_text),
            schema=EmailClassification,
            system=CLASSIFICATION_SYSTEM_PROMPT,
        )
        logger.info(
            "Classified email: category=%s urgency=%s",
            classification.category,
            classification.urgency,
        )
        return classification
