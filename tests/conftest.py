import pytest

from app.config.settings import Settings
from app.schemas.support import EmailCategory, EmailClassification, Urgency


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def settings():
    return Settings(_env_file=None, llm_api_key="test-key", llm_model="test-model")


@pytest.fixture
def classification():
    return EmailClassification(
        summary="Customer was charged twice for the Pro plan",
        category=EmailCategory.BILLING,
        urgency=Urgency.HIGH,
        customer_name="Sara",
    )
