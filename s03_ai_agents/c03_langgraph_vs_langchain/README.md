# 3.3 LangGraph vs LangChain

**One-liner:** LangChain gives you building blocks and straight-line chains;
LangGraph runs a state machine — nodes update shared state, edges (including
conditional ones) decide what runs next, and loops are allowed.

## The idea

- **Chain.** Step 1 → step 2 → step 3, always in that order. Fine for
  "retrieve then answer". No branching, no retry loop.
- **Graph.** Each node is a function that reads the state and returns the
  keys it wants to change. After a node runs, its edge picks the next node. A
  **conditional edge** is a router function that looks at the state and
  returns the next node's name — that's where "retry", "ask a human" or "done"
  decisions live.
- **State merge.** The graph, not the node, applies the update. Nodes stay
  small and testable.
- **Step limit.** Loops need a cap so a bad router can't spin forever.

You build a tiny version of both here, with no dependencies, so the mechanics
are visible.

## Why it matters

Agents loop: call a tool, check the result, maybe try again. A graph makes
that control flow explicit and testable instead of hidden in prompt text.

## Spec

Standard library only. Implement in
`s03_ai_agents/c03_langgraph_vs_langchain/example.py`, re-export `END`,
`StateGraph` and `run_chain` from `__init__.py`, add `__main__.py`, and write
`tests/s03_ai_agents/test_c03_langgraph_vs_langchain.py`.

```python
END = "__end__"

Node = Callable[[dict], dict]
Router = Callable[[dict], str]

def run_chain(steps: list[Node], state: dict) -> dict: ...

class StateGraph:
    path: list[str]   # node names visited by the last run, in order

    def add_node(self, name: str, fn: Node) -> None: ...
    def add_edge(self, src: str, dst: str) -> None: ...
    def add_conditional_edges(self, src: str, router: Router) -> None: ...
    def set_entry_point(self, name: str) -> None: ...
    def run(self, state: dict, max_steps: int = 25) -> dict: ...
```

### `run_chain`

- Start from a copy of `state`. For each step in order, merge its returned
  dict into the state (`{**state, **update}`). Return the final state.
- Never mutate the caller's dict.

### Building the graph

- `add_node`: a duplicate name or the name `END` raises `ValueError`.
- `add_edge` / `add_conditional_edges`: `src` must already be a node, else
  `ValueError`. `dst` must be a node or `END`.
- A node has at most **one** outgoing edge, plain or conditional. Adding a
  second raises `ValueError`.
- `set_entry_point`: the name must be a node, else `ValueError`.

### `run`

- No entry point set raises `ValueError`.
- Work on a copy of `state`; never mutate the caller's dict.
- Reset `path` to `[]`, then loop: append the current node to `path`, call it,
  merge its update, then pick the next node:
  - plain edge → its `dst`;
  - conditional edge → `router(state)` after the merge; a returned name that
    is neither a node nor `END` raises `ValueError`;
  - no outgoing edge → stop, as if it pointed to `END`.
- Stop when the next node is `END` and return the state.
- If more than `max_steps` nodes would run, raise `RuntimeError`.

### `main()`

Build a retry loop: `draft` increments `attempts` and sets `ok` to
`attempts >= 2`; a router sends `draft` back to itself until `ok`, then to
`END`. Print the final state and `path`. Then run the same two functions as a
chain to show it can't loop.

### Tests you should write

| Test | Assert |
|---|---|
| chain order | three steps that append to a list run in order |
| chain no mutation | caller's dict unchanged |
| linear graph | `a → b → END` returns merged state; `path == ["a", "b"]` |
| merge keeps keys | a key set by `a` and not touched by `b` survives |
| conditional branch | router sends to `yes` or `no` depending on state |
| loop until done | the `main()` retry loop ends with `attempts == 2`, `path == ["draft", "draft"]` |
| no outgoing edge ends | single node with no edge runs once |
| max steps | a router that always returns its own node raises `RuntimeError` |
| bad router target | router returning `"missing"` raises `ValueError` |
| build errors | duplicate node, edge from unknown node, second outgoing edge, missing entry point each raise `ValueError` |
| graph no mutation | caller's dict unchanged after `run` |

## Interview trap

> Q: When would you pick LangGraph over a plain chain?
> A: When the flow branches or loops — retries, tool calls until done,
> human-in-the-loop. The routing lives in code you can test, not in the prompt.

> Q: Where does human-in-the-loop go in a graph?
> A: On a conditional edge: a deterministic check on the state routes to a
> review node (or pauses the run) instead of continuing.
