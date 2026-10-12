from fastapi import APIRouter

from app.api.dependencies import SupportServiceDep
from app.api.schemas.support import SupportEmailRequest
from app.schemas.support import EmailClassification, SupportReply

router = APIRouter()


@router.post("/reply")
async def reply_to_email(
    payload: SupportEmailRequest, service: SupportServiceDep
) -> SupportReply:
    return await service.reply(payload.text)


@router.post("/classify")
async def classify_email(
    payload: SupportEmailRequest, service: SupportServiceDep
) -> EmailClassification:
    return await service.classify(payload.text)
