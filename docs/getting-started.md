# Getting started

This guide installs the current development version and runs one semantic
routing decision.

## Requirements

- Python 3.11 or newer
- A TypeSafe API key
- A checkout of this repository while the package is in pre-release development

## Install from the repository

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Editable installation means changes under `src/typesafe_decisions` are used
without reinstalling the package.

## Configure TypeSafe

Set the API key in the default environment variable:

```bash
export TYPESAFE_API_KEY="your-api-key"
```

Do not commit API keys to the repository. `api_key_env` accepts an environment
variable **name**, not a literal secret:

```python
decisions = DecisionClient(api_key_env="MY_TYPESAFE_API_KEY")
```

## Make a decision

Create `example.py`:

```python
from typesafe_decisions import DecisionClient


ticket = "I was charged twice for the same order."

with DecisionClient() as decisions:
    team = decisions.match(
        ticket,
        "Which team should handle this ticket?",
        {
            "Billing": "Charges, invoices, and payment problems",
            "Returns": "Refunds, exchanges, and damaged items",
            "Shipping": "Delivery status, delays, and lost packages",
        },
    )

print(f"Route to: {team}")
```

Run it:

```bash
python example.py
```

`match()` returns the selected dictionary key, so the result can be used
directly in application routing.

## Resource lifetime

Prefer the context-manager form:

```python
with DecisionClient() as decisions:
    result = decisions.match(...)
```

It closes the underlying HTTP client even when the block raises an exception.

## Continue

- Use [`feels()`](guides/feels.md) for a score instead of a label.
- Learn how to design [`match()` criteria](guides/match.md).
- Configure the independent [Cloudflare `llm()` helper](guides/cloudflare-llm.md).
