from typing import Annotated

from fastapi import Depends, Request

from app.services.llm_client import LLMClient
from app.services.support_service import SupportService


def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client


LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]


def get_support_service(llm_client: LLMClientDep) -> SupportService:
    return SupportService(llm_client)


SupportServiceDep = Annotated[SupportService, Depends(get_support_service)]
