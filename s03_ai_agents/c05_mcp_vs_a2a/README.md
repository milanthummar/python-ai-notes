# 3.5 MCP vs A2A

**One-liner:** MCP connects an agent to **tools and data** (agent → server);
A2A connects an agent to **another agent** (agent → agent), with a task that
moves through states.

## The idea

- **MCP (Model Context Protocol).** A server exposes tools, resources and
  prompts over JSON-RPC 2.0. The client asks `tools/list`, then `tools/call`.
  It's 3.4's dispatcher turned into a standard protocol, so any MCP client can
  use any MCP server.
- **A2A (Agent2Agent).** One agent hands a **task** to another agent, which
  works on it, may ask for more input, and eventually completes or fails. The
  remote agent is opaque: you see its card (what it can do) and the task
  state, not its tools.
- **Rule of thumb.** Calling a function with known inputs → MCP. Delegating a
  goal to something that plans on its own → A2A.

Two details worth knowing:

- In MCP, a tool that **runs but fails** is a normal result with
  `isError: true`, so the model can read it. Protocol problems (unknown
  method, bad params) are JSON-RPC **errors**.
- A2A tasks have a lifecycle; only some state changes are legal.

## Why it matters

Questions like "how would your agent call our internal service?" (MCP) and
"how would two teams' agents cooperate?" (A2A) need the right protocol
picked first.

## Spec

Standard library only. Implement in `s03_ai_agents/c05_mcp_vs_a2a/example.py`,
re-export `McpServer` and `Task` from `__init__.py`, add `__main__.py`, and
write `tests/s03_ai_agents/test_c05_mcp_vs_a2a.py`.

```python
class McpServer:
    def add_tool(self, name: str, description: str, fn: Callable[..., Any]) -> None: ...
    def handle(self, request: dict) -> dict: ...

@dataclass
class Task:
    id: str
    state: str = "submitted"
    history: list[str] = field(default_factory=list)

    def transition(self, new_state: str) -> None: ...
```

### `McpServer.handle`

Every response has `"jsonrpc": "2.0"` and the request's `"id"` (or `None` if
missing), plus **either** `"result"` **or** `"error": {"code", "message"}`.

| Request | Response |
|---|---|
| not `"jsonrpc": "2.0"`, or `"method"` missing / not a string | error `-32600` (Invalid Request) |
| `method == "tools/list"` | result `{"tools": [{"name", "description"}, ...]}` in the order added |
| `method == "tools/call"` with `params = {"name": ..., "arguments": {...}}` | call `fn(**arguments)`; result `{"content": [{"type": "text", "text": str(output)}], "isError": False}` |
| `tools/call` with a missing or unknown `name`, or `arguments` not a dict | error `-32602` (Invalid params) |
| `tools/call` where the tool raises | result with `"isError": True` and the exception message as the text — **not** a JSON-RPC error |
| any other method | error `-32601` (Method not found) |

- Missing `"arguments"` means `{}`.
- `add_tool` with a duplicate name raises `ValueError`.
- `handle` never raises.

### `Task.transition`

Allowed transitions:

| From | To |
|---|---|
| `submitted` | `working`, `canceled` |
| `working` | `input-required`, `completed`, `failed`, `canceled` |
| `input-required` | `working`, `canceled` |
| `completed`, `failed`, `canceled` | nothing (terminal) |

- A legal transition appends the **old** state to `history`, then sets
  `state`.
- Anything else raises `ValueError` and leaves `state` and `history`
  unchanged.

### `main()`

Add an `add(a, b)` tool, print a `tools/list` response, a good `tools/call`,
and a `tools/call` whose tool raises. Then walk a `Task` through
`submitted → working → input-required → working → completed` and print its
history.

### Tests you should write

| Test | Assert |
|---|---|
| response envelope | every response has `jsonrpc == "2.0"` and the same `id` |
| tools/list | names and descriptions in the order added |
| tools/call ok | `add(2, 3)` → text `"5"`, `isError is False` |
| tool raises | `result.isError is True`, no `"error"` key |
| unknown tool | error code `-32602` |
| bad arguments type | `arguments=[]` → `-32602` |
| unknown method | `-32601` |
| invalid request | missing `jsonrpc` or `method` → `-32600` |
| duplicate tool | `add_tool` twice → `ValueError` |
| task happy path | the `main()` walk ends `completed` with history of the four earlier states |
| task illegal | `submitted → completed` raises `ValueError`; state and history unchanged |
| task terminal | any transition from `completed` raises `ValueError` |
| task default history | two tasks don't share the same `history` list |

## Interview trap

> Q: MCP or A2A for letting our agent query the billing service?
> A: MCP: it's a tool call with known inputs. A2A is for delegating a goal to
> another agent that decides its own steps.

> Q: A tool raised an exception. Is that a JSON-RPC error?
> A: No. The call itself worked, so it's a result with `isError: true` that
> the model can read and react to. JSON-RPC errors are for protocol problems.
