# Application examples

These examples show how semantic decisions fit into ordinary application
control flow. They are starting points: evaluate the criteria and thresholds
against representative data before using them in production.

## Route a support ticket

Use `match()` when the possible destinations are known in advance. The returned
value is one of the dictionary keys, so it can be used directly as a queue or
workflow identifier.

```python
from typesafe_decisions import DecisionClient


ticket = {
    "subject": "Wrong shoe size",
    "message": "My shoes arrived in size 41, but I ordered size 43.",
}

queues = {
    "billing": "Charges, invoices, and payment problems",
    "returns": "Exchanges, refunds, wrong items, and damaged items",
    "shipping": "Delivery status, delays, and lost packages",
}

with DecisionClient() as decisions:
    queue = decisions.match(
        ticket,
        "Which support queue should handle this ticket?",
        queues,
    )

print(f"Send to queue: support:{queue}")
```

## Escalate an urgent message

Use `feels()` when the application needs a score and owns the policy that turns
that score into an action.

```python
from typesafe_decisions import DecisionClient


message = "Payroll closes in an hour and I still cannot approve the transfer."

with DecisionClient() as decisions:
    urgency = decisions.feels(message, "needs immediate human attention")

if urgency >= 0.8:
    action = "page-on-call"
elif urgency >= 0.5:
    action = "priority-review"
else:
    action = "normal-queue"

print(f"Action: {action} (urgency={urgency:.2f})")
```

The thresholds are application policy, not universal defaults. Choose them
from evaluations on inputs that represent the real workload.

## Draft a reply after routing

Decisions and text generation can be combined while remaining separate steps.
Here, TypeSafe selects the team and Cloudflare receives only the context passed
through `using`.

```python
from typesafe_decisions import DecisionClient, llm


customer_message = "Where is my parcel? It should have arrived last week."

with DecisionClient() as decisions:
    team = decisions.match(
        customer_message,
        "Which team should handle this message?",
        {
            "billing": "Charges, invoices, and payment problems",
            "returns": "Refunds, exchanges, and damaged items",
            "shipping": "Delivery status, delays, and lost packages",
        },
    )

reply = llm(
    "Draft a calm acknowledgement in one sentence. Do not promise a resolution.",
    using={
        "customer_message": customer_message,
        "assigned_team": team,
    },
    temperature=0.2,
)

print(f"Assigned team: {team}")
print(f"Draft reply: {reply}")
```

This final example needs both the TypeSafe configuration from
[Getting started](getting-started.md) and the Cloudflare settings from the
[`llm()` guide](guides/cloudflare-llm.md).
