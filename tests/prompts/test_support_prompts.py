from app.prompts.support import (
    REPLY_GUIDELINES,
    REPLY_SYSTEM_PROMPT,
    build_email_prompt,
    build_reply_prompt,
    build_reply_system_prompt,
)
from app.schemas.support import EmailCategory


def test_every_category_has_reply_guidelines():
    assert set(REPLY_GUIDELINES) == set(EmailCategory)


def test_email_prompt_strips_and_wraps_text():
    assert build_email_prompt("  hello  ") == "<email>\nhello\n</email>"


def test_reply_system_prompt_adds_only_its_category_guidelines():
    prompt = build_reply_system_prompt(EmailCategory.BILLING)

    assert prompt.startswith(REPLY_SYSTEM_PROMPT)
    assert REPLY_GUIDELINES[EmailCategory.BILLING] in prompt
    assert REPLY_GUIDELINES[EmailCategory.TECHNICAL] not in prompt


def test_reply_prompt_includes_classification_and_email(classification):
    prompt = build_reply_prompt("charged twice", classification)

    assert f"Summary: {classification.summary}" in prompt
    assert "Urgency: high" in prompt
    assert "Customer name: Sara" in prompt
    assert prompt.endswith("<email>\ncharged twice\n</email>")


def test_reply_prompt_marks_missing_name_as_unknown(classification):
    anonymous = classification.model_copy(update={"customer_name": None})

    assert "Customer name: unknown" in build_reply_prompt("hi", anonymous)
