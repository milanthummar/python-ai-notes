# 3.4 Tool calling

**One-liner:** The model never runs your code. It returns a tool name and JSON
arguments; your code validates them, runs the function, and hands the result
(or a readable error) back.

## The idea

1. You send the model a list of tool **schemas**: name, description, and a
   JSON Schema for the arguments.
2. The model replies with a call: `{"tool": "get_weather", "args": {...}}`.
3. Your **dispatcher** parses it, looks up the tool, validates the args with
   Pydantic (2.1 — args from an LLM are untrusted input), and runs it.
4. Every failure — bad JSON, unknown tool, invalid args, the tool itself
   raising — becomes an error **result**, not an exception. The model reads
   the error and can retry with a fixed call.

## Why it matters

Tool calls are where an agent touches real systems. A dispatcher that
validates first and never crashes the loop is the difference between a
recoverable mistake and a 500.

## Spec

Depends on `pydantic>=2`. Implement in `s03_ai_agents/c04_tool_calling/example.py`,
re-export `ToolResult` and `ToolRegistry` from `__init__.py`, add
`__main__.py`, and write `tests/s03_ai_agents/test_c04_tool_calling.py`.

```python
class ToolResult(BaseModel):
    ok: bool
    output: Any = None
    error: str | None = None

class ToolRegistry:
    def tool(self, name: str, args_model: type[BaseModel]) -> Callable: ...
    def schemas(self) -> list[dict]: ...
    def dispatch(self, raw: str) -> ToolResult: ...
```

### `tool` (decorator)

```python
registry = ToolRegistry()

@registry.tool("get_weather", WeatherArgs)
def get_weather(args: WeatherArgs) -> str:
    """Current weather for a city."""
    ...
```

- Registers the function under `name` with its args model, and returns the
  function unchanged so it can still be called directly.
- The description is the first line of the function's docstring, or `""`.
- Registering the same name twice raises `ValueError`.

### `schemas`

- One dict per tool, in registration order:
  `{"name": ..., "description": ..., "parameters": args_model.model_json_schema()}`.

### `dispatch`

Never raises. Steps, in order — the first failure returns
`ToolResult(ok=False, error=...)` with the error **starting with** the prefix
shown:

| Step | Failure | Error prefix |
|---|---|---|
| `json.loads(raw)` | not valid JSON | `invalid json:` |
| shape | not an object, `"tool"` missing or not a string, or `"args"` present but not an object | `invalid call:` |
| lookup | no tool with that name | `unknown tool:` (followed by the name) |
| validate | `args_model.model_validate(args)` raises `ValidationError` | `invalid args:` |
| run | the tool function raises any `Exception` | `tool failed:` |

- Missing `"args"` means `{}`.
- Success returns `ToolResult(ok=True, output=<return value>)` with
  `error=None`.

### `main()`

Register `get_weather` with `WeatherArgs(city: str = Field(min_length=1),
unit: Literal["c", "f"] = "c")` returning a fake string. Print the schemas,
then dispatch one good call and one call of each failure kind.

### Tests you should write

| Test | Assert |
|---|---|
| decorator returns fn | the decorated function can still be called directly |
| duplicate name | second registration raises `ValueError` |
| schemas | name, first docstring line, and `parameters["properties"]` contains `"city"` |
| happy path | `ok is True`, `output` is the tool's return value, `error is None` |
| default args | `{"tool": "ping"}` with no `"args"` works for a tool whose model has no required fields |
| invalid json | `"not json"` → `ok is False`, error starts with `invalid json:` |
| invalid call | `[]`, `{"args": {}}`, and `{"tool": "x", "args": []}` → `invalid call:` |
| unknown tool | error starts with `unknown tool:` and contains the name |
| invalid args | `unit="kelvin"` → `invalid args:` |
| tool raises | a tool that raises `RuntimeError` → `tool failed:`; `dispatch` itself does not raise |

## Interview trap

> Q: The model called a tool with bad arguments. What happens?
> A: Validation fails before the tool runs, and the error goes back to the
> model as the tool result so it can correct the call. The agent loop keeps
> going.

> Q: Who executes the tool — the model or your code?
> A: Your code. The model only proposes a call; you decide whether and how it
> runs.
