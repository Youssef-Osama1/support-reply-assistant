from typing import Annotated

from pydantic import BaseModel, StringConstraints

EmailText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)
]


class SupportEmailRequest(BaseModel):
    text: EmailText
