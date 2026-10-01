# Pydantic at the edges

**One-liner:** Validate untrusted input at the boundary — tool args, API
payloads — and fail fast. Inside the system, trust the model you already
parsed.

## The idea

Anything that crossed a boundary is untrusted: an LLM tool call, an HTTP body,
a service response. Parse it into a Pydantic model there. A bad payload raises
`ValidationError` before any work runs.

- `extra="forbid"` rejects unexpected keys instead of silently ignoring them.
- `Field(...)` constrains one value (`min_length`, `ge`, `le`).
- `field_validator` checks or reshapes **one** field. `mode="before"` runs
  before Pydantic's own parsing, so you can turn a string into a number.
- `model_validator(mode="after")` sees the whole object, so it can enforce a
  rule that depends on more than one field.

## Why it matters

An LLM is a black box to your tool. The arguments it emits are untrusted, same
as user input. Validating at the edge spends nothing on a bad call and keeps
the rest of the code free of defensive checks.

## Spec

Add `pydantic>=2` to `[project].dependencies` in `pyproject.toml`, then
`uv sync`.

Implement `LookupArgs` and `AnswerArgs` in
`ch06_pydantic_at_the_edges/example.py` and re-export them from
`ch06_pydantic_at_the_edges/__init__.py`. You write
`tests/test_ch06_pydantic_at_the_edges.py`. Register the package in
`pyproject.toml` when it exists.

Files to create, same layout as earlier chapters:

| File | Contents |
|---|---|
| `example.py` | `LookupArgs`, `AnswerArgs`, `main()` |
| `__init__.py` | Re-exports both models in `__all__` |
| `__main__.py` | `from ch06_pydantic_at_the_edges.example import main` then `main()` |

`main()` prints one valid `AnswerArgs` and one caught `ValidationError`, so
`uv run python -m ch06_pydantic_at_the_edges` shows both paths.

Both models use:

```python
model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

### `LookupArgs`

| Field | Rule |
|---|---|
| `intent: str` | `Field(min_length=1)` after stripping. `field_validator` allows only `"access"` and `"billing"`. Anything else raises `ValidationError`. |

Observable behavior:

- `LookupArgs(intent=" access ")` succeeds and `intent == "access"`.
- `intent=""` or whitespace-only fails.
- `intent="other"` fails.
- `LookupArgs(intent="access", hack=True)` fails (`extra="forbid"`).

Strip whitespace **before** the allowed-value check, so `" access "` is valid.

### `AnswerArgs`

| Field | Rule |
|---|---|
| `question: str` | `Field(min_length=1)` after stripping. |
| `confidence: float` | `Field(ge=0, le=1)`. A `field_validator(..., mode="before")` accepts a numeric string (`"0.9"`) and returns a `float`. Non-numeric strings fail. |
| `citations: list[str]` | Defaults to a new empty list via `Field(default_factory=list)`, not `= []`. |

Cross-field rule, `model_validator(mode="after")`:

- If `confidence >= 0.8`, `citations` must contain at least one item.
- Below `0.8`, empty citations are valid.
- The validator returns `self`.

Observable behavior:

- `AnswerArgs(question=" hi ", confidence="0.9", citations=["kb-1"])` succeeds,
  `question == "hi"`, `confidence == 0.9` (a float), `citations == ["kb-1"]`.
- `confidence=1.5` or `confidence=-0.1` fails.
- `confidence="nope"` fails.
- `confidence=0.9` with `citations=[]` fails.
- `confidence=0.8` with `citations=[]` fails (the bar is inclusive).
- `confidence=0.79` with `citations=[]` succeeds.
- An extra key fails.
- Two instances that omit `citations` do not share the same list object.

Do not add fields or rules beyond these.

### Tests you should write

One test per row above is enough. Import `ValidationError` from `pydantic` and
use `pytest.raises(ValidationError)` for the failures.

## Interview trap

> Q: When do you validate — every function, or at the boundary?
> A: At the boundary. Tool args and API payloads are untrusted. Once a model
> has parsed them, downstream code can trust the type.

> Q: `field_validator` vs `model_validator`?
> A: One field vs the whole model. Cross-field rules ("high confidence requires
> a citation") belong on `model_validator`.
