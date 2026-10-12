from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import LLMOutputError
from app.prompts.support import (
    CLASSIFICATION_SYSTEM_PROMPT,
    REPLY_GUIDELINES,
    build_reply_prompt,
    build_reply_system_prompt,
)
from app.schemas.support import EmailCategory, EmailClassification, SupportReply
from app.services.llm_client import LLMClient
from app.services.support_service import SupportService

pytestmark = pytest.mark.anyio


@pytest.fixture
def llm_client(classification):
    client = AsyncMock(spec=LLMClient)
    client.extract.return_value = classification
    client.complete.return_value = "  Hi Sara, we are on it.  "
    return client


@pytest.fixture
def service(llm_client):
    return SupportService(llm_client)


async def test_classify_wraps_email_and_sends_schema(service, llm_client):
    await service.classify("  charged twice  ")

    llm_client.extract.assert_awaited_once_with(
        prompt="<email>\ncharged twice\n</email>",
        schema=EmailClassification,
        system=CLASSIFICATION_SYSTEM_PROMPT,
    )


async def test_reply_returns_classification_and_stripped_reply(service, classification):
    result = await service.reply("charged twice")

    assert result == SupportReply(
        classification=classification, reply="Hi Sara, we are on it."
    )


async def test_reply_builds_prompts_from_classification(
    service, llm_client, classification
):
    await service.reply("charged twice")

    llm_client.complete.assert_awaited_once_with(
        prompt=build_reply_prompt("charged twice", classification),
        system=build_reply_system_prompt(EmailCategory.BILLING),
    )


@pytest.mark.parametrize("category", list(EmailCategory))
async def test_reply_routes_to_category_guidelines(
    service, llm_client, classification, category
):
    llm_client.extract.return_value = classification.model_copy(
        update={"category": category}
    )

    await service.reply("some email")

    system = llm_client.complete.await_args.kwargs["system"]
    assert REPLY_GUIDELINES[category] in system


async def test_blank_reply_raises_llm_output_error(service, llm_client):
    llm_client.complete.return_value = "   "

    with pytest.raises(LLMOutputError):
        await service.reply("charged twice")
