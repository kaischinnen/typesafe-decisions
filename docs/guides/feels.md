# Measure a semantic property

Use `feels()` when the application needs a score rather than a category.

```python
from typesafe_decisions import DecisionClient


email = "Please resolve this before payroll closes today."

with DecisionClient() as decisions:
    urgency = decisions.feels(email, "needs an urgent reply")

if urgency > 0.7:
    print("Escalate")
```

## Choose a useful question

Ask about one property that can vary by degree:

- `"needs an urgent reply"`
- `"contains hostile language"`
- `"is likely to be a duplicate"`

Avoid combining multiple policies in one question. Measure them separately when
the application needs separate thresholds or explanations.

## Set thresholds from real data

The value `0.7` above is an example, not a universal default. Collect
representative inputs, decide which mistakes are more costly, and select a
threshold from those results.

## Override request controls

Defaults are configured on `DecisionClient`; individual calls can override
them:

```python
import httpx2
from typesafe_sdk import RetryPolicy

score = decisions.feels(
    email,
    "needs an urgent reply",
    model="jev-latest",
    retry=RetryPolicy(max_retries=2),
    timeout=httpx2.Timeout(5.0),
    extra_headers={"x-trace-id": "ticket-123"},
    extra_body={"metadata": {"source": "support"}},
)
```

See [`DecisionClient.feels`](../reference.md#typesafe_decisions.DecisionClient.feels)
for the complete signature.
