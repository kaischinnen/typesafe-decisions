# Concepts

`typesafe-decisions` separates machine-readable decisions from generated text.
This distinction keeps application control flow explicit.

## Semantic decisions

`DecisionClient` delegates decision requests to TypeSafe System One and exposes
two high-level operations:

- `feels()` measures one semantic property and returns a score.
- `match()` chooses one label from criteria supplied by the application.

The application still owns the policy. For example, the model can provide an
urgency score, while your code decides whether `0.7` is the correct escalation
threshold.

## Criteria are part of the contract

For `match()`, dictionary keys are stable values used by the program and the
dictionary values explain their meaning:

```python
teams = {
    "billing": "Charges, invoices, refunds, and payment problems",
    "shipping": "Delivery status, delays, and lost packages",
}
```

Use concise keys and criteria that are distinct enough to choose between. When
a key is already self-explanatory, its value may be `None`.

## Text generation is separate

The standalone `llm()` helper does not call TypeSafe. It sends a writing
instruction to Cloudflare AI Gateway and returns text.

```python
reply = llm(
    "Draft a calm reply in one sentence.",
    using={"ticket": "Where is my package?"},
)
```

`using` is the only optional context added to the instruction. The helper does
not read a `DecisionClient`, conversation, or other application state
implicitly.

## Types and runtime validation

The package includes `py.typed`, so type checkers can consume its annotations.
`match()` is overloaded: it returns `str` normally and the selected Pydantic
model type when `response_model` is supplied.

Types improve integration safety, but semantic behavior still needs evaluation
against representative application data before production use.
