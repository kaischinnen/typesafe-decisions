# typesafe-decisions

**Small, typed building blocks for semantic decisions in Python.**

`typesafe-decisions` is an experimental convenience layer around TypeSafe
System One. It turns semantic judgments into ordinary Python values that an
application can use for routing, thresholds, and other decisions.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](reference.md){ .md-button }

!!! warning "Experimental and unofficial"

    This project is not an official TypeSafe SDK. It is pre-release software,
    and its public API may change.

## Choose the right operation

| Operation | Use it when you need | Result |
| --- | --- | --- |
| `DecisionClient.feels()` | A semantic score for one property | `float` |
| `DecisionClient.match()` | The best label from explicit criteria | `str` or a Pydantic model |
| `llm()` | Generated text through Cloudflare AI Gateway | `str` |

The first two operations use TypeSafe System One. The standalone `llm()` helper
is independent and sends only its instruction and explicitly supplied context
to Cloudflare.

## Small public interface

```python
from typesafe_decisions import DecisionClient, llm
```

The package exports these two names deliberately. Configuration and advanced
request controls remain available without expanding the common call path.

## Next steps

- Follow [Getting started](getting-started.md) for a first routing decision.
- Adapt the complete [application examples](examples.md) for support routing,
  escalation, and response drafting.
- Read [Concepts](concepts.md) to understand the boundary between decisions and
  text generation.
- Use the task-focused [guides](guides/match.md) for concrete patterns.
