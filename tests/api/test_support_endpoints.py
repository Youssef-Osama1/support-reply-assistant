from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_support_service
from app.core.exceptions import LLMOutputError
from app.main import app
from app.schemas.support import SupportReply
from app.services.support_service import SupportService


@pytest.fixture
def support_reply(classification):
    return SupportReply(classification=classification, reply="Hi Sara")


@pytest.fixture
def service(classification, support_reply):
    fake = AsyncMock(spec=SupportService)
    fake.classify.return_value = classification
    fake.reply.return_value = support_reply
    app.dependency_overrides[get_support_service] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_reply_returns_classification_and_reply(client, service, support_reply):
    response = client.post("/support/reply", json={"text": "charged twice"})

    assert response.status_code == 200
    assert response.json() == support_reply.model_dump(mode="json")
    service.reply.assert_awaited_once_with("charged twice")


def test_classify_skips_the_reply_call(client, service, classification):
    response = client.post("/support/classify", json={"text": "charged twice"})

    assert response.status_code == 200
    assert response.json() == classification.model_dump(mode="json")
    service.reply.assert_not_awaited()


@pytest.mark.parametrize("path", ["/support/reply", "/support/classify"])
@pytest.mark.parametrize("text", ["   ", "x" * 10_001])
def test_invalid_text_is_rejected_before_the_service(client, service, path, text):
    response = client.post(path, json={"text": text})

    assert response.status_code == 422
    service.reply.assert_not_awaited()
    service.classify.assert_not_awaited()


def test_bad_model_output_returns_502(client, service):
    service.reply.side_effect = LLMOutputError("Model returned an empty reply")

    response = client.post("/support/reply", json={"text": "charged twice"})

    assert response.status_code == 502
    assert response.json() == {"detail": "Model returned an empty reply"}
