# typesafe-decisions

**Small, typed building blocks for semantic decisions in Python.**

[![Tests](https://github.com/kaischinnen/TypeSafe-Wrapper/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/kaischinnen/TypeSafe-Wrapper/actions/workflows/tests.yml)
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

## Development

Create a virtual environment, install the project in editable mode, and run
the test suite from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest
```

The source lives in `src/typesafe_decisions`, the executable example remains
in `demo.py`, and tests live in `tests`.
