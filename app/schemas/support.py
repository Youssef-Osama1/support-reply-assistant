from enum import StrEnum

from pydantic import BaseModel, Field


class EmailCategory(StrEnum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    OTHER = "other"


class Urgency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EmailClassification(BaseModel):
    summary: str = Field(
        description="The single category that best fits the main request"
    )
    category: EmailCategory = Field(
        description="The single category that best fits the main request"
    )
    urgency: Urgency = Field(
        description="high if the customer is blocked, losing money or about to "
        "leave; low for questions and suggestions; medium otherwise"
    )
    customer_name: str | None = Field(
        description="Customer name as signed in the email, null if not stated"
    )


class SupportReply(BaseModel):
    classification: EmailClassification
    reply: str
