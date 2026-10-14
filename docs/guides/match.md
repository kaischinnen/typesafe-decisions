# Choose the best match

Use `match()` when the application must select one value from a known set.

```python
from typesafe_decisions import DecisionClient


teams = {
    "billing": "Charges, invoices, and payment problems",
    "returns": "Exchanges, refunds, wrong items, and damaged items",
    "shipping": "Delivery status, delays, and lost packages",
}

with DecisionClient() as decisions:
    team = decisions.match(
        "My shoes arrived in the wrong size.",
        "Which team should handle this ticket?",
        teams,
    )
```

By default, the return value is exactly one of the keys in `teams`.

## Design clear criteria

Good criteria are:

- mutually distinguishable;
- written in the language of the input domain;
- specific about ambiguous boundary cases;
- backed by an explicit fallback category when the domain needs one.

```python
categories = {
    "account": "Login, access, profile, or account settings",
    "payment": "Card failures, charges, receipts, or invoices",
    "other": "Anything that does not fit the other categories",
}
```

## Parse the response with a custom model

Pass a Pydantic model when downstream code needs selected fields from the raw
System One response:

```python
from typing import Literal

from pydantic import BaseModel


class MatchAnswer(BaseModel):
    choice: Literal["billing", "returns", "shipping"]
    confidence: float
    probabilities: dict[str, float]


class MatchResponse(BaseModel):
    model: str
    answers: dict[str, MatchAnswer]


with DecisionClient() as decisions:
    result = decisions.match(
        "My parcel has not moved for a week.",
        "Which team should handle this ticket?",
        teams,
        response_model=MatchResponse,
    )

print(result.answers["match"].choice)
print(result.answers["match"].confidence)
```

`response_model` controls how the existing API response is validated and
parsed; it does not ask the model to generate arbitrary additional fields. The
underlying TypeSafe SDK creates the model instance, and `typesafe-decisions`
returns it unchanged.

See [`DecisionClient.match`](../reference.md#typesafe_decisions.DecisionClient.match)
for request-level overrides and the complete signature.
