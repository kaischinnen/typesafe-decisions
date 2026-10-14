# Generate text through Cloudflare

`llm()` is a small, independent text-generation helper. It uses Cloudflare AI
Gateway rather than TypeSafe System One.

## Configure Cloudflare

The two required settings are:

```bash
export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="your-api-token"
```

Optional settings:

```bash
export GATEWAY_ID="default"
export TEXT_MODEL="@cf/meta/llama-3.1-8b-instruct-fp8"
```

All four settings can also be passed explicitly to `llm()`.

## Supply explicit context

```python
from typesafe_decisions import llm


reply = llm(
    "Draft a calm, helpful reply in one short sentence.",
    using={
        "customer_message": "Where is my parcel? It is a week late.",
        "delivery_status": "Delayed at regional depot",
    },
)

print(reply)
```

The request contains the instruction plus `using` as context. If `using` is
omitted, only the instruction is sent as the user payload.

## Override generation controls

```python
reply = llm(
    "Summarize the incident in two sentences.",
    using=incident,
    gateway_id="support-tools",
    model="@cf/meta/llama-3.1-8b-instruct-fp8",
    max_tokens=180,
    temperature=0.2,
    timeout=10.0,
)
```

The helper returns stripped text. Configuration failures, HTTP failures, invalid
responses, and missing generated text raise `RuntimeError`.

See [`llm`](../reference.md#typesafe_decisions.llm) for the complete signature.
