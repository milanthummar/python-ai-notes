# TypedDict vs dataclass vs Pydantic

**One-liner:** TypedDict is a type hint for a dict and disappears at runtime.
A dataclass holds data with no validation. Pydantic validates at the boundary.

## The idea

Same shape, three different runtimes:

| | TypedDict | dataclass | Pydantic `BaseModel` |
|---|---|---|---|
| Runtime object | the original `dict` | a real instance | a real instance |
| Extra keys | kept | ignored by our constructor | rejected |
| Wrong types | accepted | accepted | rejected (`strict=True`) |
| Use when | annotating a dict you already trust, e.g. LangGraph state | a small in-process record | untrusted input at the edge |

## Why it matters

Picking the heavy tool for internal state adds noise. Picking the light tool
for untrusted input lets bad data through. The choice is about **where the
data came from**, not which syntax you like.

## Spec

Depends on `pydantic>=2` (same dependency as chapter 06).

Implement the three types and three constructors in
`ch07_typeddict_vs_dataclass_vs_pydantic/example.py`. Re-export all six names
from the package `__init__.py`. You write
`tests/test_ch07_typeddict_vs_dataclass_vs_pydantic.py`. Register the package
in `pyproject.toml` when it exists.

```python
class AgentStateTD(TypedDict):
    question: str
    retries: int

@dataclass
class AgentStateDC:
    question: str
    retries: int = 0

class AgentStateModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    question: str
    retries: int = 0

def from_dict_typed(data: dict) -> AgentStateTD: ...

def from_dict_dataclass(data: dict) -> AgentStateDC: ...

def from_dict_model(data: dict) -> AgentStateModel: ...
```

`strict=True` is required. In lax mode Pydantic would coerce `"3"` into `3`,
which hides the point of this chapter.

### `from_dict_typed`

- No runtime check. Return the **same** dict object (`result is data`).
- Extra keys stay. Missing keys are not filled in. Wrong types are kept.

### `from_dict_dataclass`

- Build an `AgentStateDC` from `question` and `retries`.
- Missing `retries` defaults to `0`.
- Missing `question` raises `KeyError`.
- Extra keys are **ignored**, not an error.
- Types are **not** validated: `retries="nope"` is stored as the string
  `"nope"`.

### `from_dict_model`

- `AgentStateModel.model_validate(data)`.
- Missing `retries` defaults to `0`.
- Missing `question` raises `ValidationError`.
- Extra keys raise `ValidationError`.
- Wrong types raise `ValidationError` (`retries="3"` fails; `retries=3` works).
- `question` must already be a `str` (`strict=True` — do not coerce).

### Tests you should write

| Test | Assert |
|---|---|
| typed identity | `from_dict_typed(data) is data` |
| typed keeps extras | input `{"question": "q", "retries": 1, "hack": True}` still has `"hack"` |
| dataclass default | `{"question": "q"}` → `retries == 0` and `isinstance(..., AgentStateDC)` |
| dataclass ignores extra | extra key does not raise; `question` and `retries` are set |
| dataclass does not validate | `retries="nope"` is stored as `"nope"` |
| dataclass missing question | `KeyError` |
| model default | `{"question": "q"}` → `retries == 0` |
| model rejects extra | `ValidationError` |
| model rejects wrong type | `retries="3"` → `ValidationError` |
| model accepts good payload | `question="q"`, `retries=2` round-trips |
| model missing question | `ValidationError` |

## Interview trap

> Q: Why not use Pydantic for everything, including LangGraph state?
> A: State is internal and already trusted — a TypedDict (or dataclass) is
> enough and stays a plain dict the graph can merge. Pydantic earns its cost
> at the edges, where input is untrusted.
