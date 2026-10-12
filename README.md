# Support Reply Assistant

Classify customer support emails and draft a reply with an LLM.

Send a customer email and get back its category, urgency and a reply written for that category.

## How It Works

1. **Classify**: the model fills `EmailClassification` (summary, category, urgency, customer name).
2. **Route**: the category picks its reply guidelines (billing, technical, account, feature request, other).
3. **Reply**: the model drafts a reply from those guidelines, the classification and the original email.

## Quick Start

```bash
uv sync
cp .env.example .env    # add your LLM_API_KEY
uv run uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs.

## Usage

```bash
curl -X POST http://localhost:8000/support/reply \
  -H "Content-Type: application/json" \
  -d '{"text": "Hi, I was charged twice this month (invoice INV-2291). Thanks, Sara"}'
```

`POST /support/classify` takes the same body and returns only the classification, with one model call instead of two.

| Status | Meaning |
|--------|---------|
| 200 | Classification and reply |
| 422 | Empty text or text longer than 10,000 characters |
| 502 | The model returned output that does not match the schema, or an empty reply |

## Development

```bash
uv run pytest                                        # tests, no network access
uv run python -m evals.run_support                   # evals against the real model
uv run python -m playground.try_support              # one email through the full chain
```

The evals run every case in `evals/support_cases.jsonl` three times and print the pass
rate for the classification and for rule checks on the reply (language, length, sign-off,
no markdown, no forbidden promises). Run them after changing a prompt, the schema or the model.

## Project Structure

```text
├── app/
│   ├── api/          # Routes, dependencies and request/response models
│   ├── config/       # Settings loaded from .env
│   ├── core/         # Logging and exceptions
│   ├── prompts/      # Classification and reply prompts
│   ├── schemas/      # Pydantic models the LLM fills in
│   ├── services/     # LLM client and support service
│   └── main.py       # FastAPI app entry point
├── docker/           # Docker configurations
├── docs/             # Documentation files
├── evals/            # Eval cases and runner for output quality
├── playground/       # Experimental code, never imported by app/
├── tests/            # Tests that run without network access
├── .env.example      # Environment variables template
├── pyproject.toml    # Project dependencies and metadata
└── uv.lock           # Locked dependencies
```
