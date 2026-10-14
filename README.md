# typesafe-decisions

**Small, typed building blocks for semantic decisions in Python.**

[![Tests](https://github.com/kaischinnen/typesafe-decisions/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/kaischinnen/typesafe-decisions/actions/workflows/tests.yml)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Status: Experimental](https://img.shields.io/badge/status-experimental-F59E0B)

`typesafe-decisions` is an experimental convenience layer around TypeSafe
System One. It turns semantic judgments into ordinary Python values that an
application can use for routing, thresholds, and other decisions.

The project currently contains a `DecisionClient` for TypeSafe-backed
decisions and a small, independent `llm()` helper for text generation through
Cloudflare AI Gateway.

> [!WARNING]
> This project is unofficial, pre-release software. Its public API may change.

## Quick start

Install the current development version from a checkout:

```bash
python -m pip install -e .
export TYPESAFE_API_KEY="your-api-key"
```

```python
from typesafe_decisions import DecisionClient

with DecisionClient() as decisions:
    team = decisions.match(
        "I was charged twice for the same order.",
        "Which team should handle this ticket?",
        {
            "Billing": "Charges, invoices, and payment problems",
            "Returns": "Refunds, exchanges, and damaged items",
        },
    )

print(team)
```

See the [documentation](https://kaischinnen.github.io/typesafe-decisions/)
for setup, [application examples](https://kaischinnen.github.io/typesafe-decisions/examples/),
concepts, guides, and the API reference.

## Development

Create a virtual environment, install the project in editable mode, and run
the test suite from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[docs]"
python -m unittest
zensical build --clean
```

The source lives in `src/typesafe_decisions`, documentation examples live in
`docs`, and tests live in `tests`.
