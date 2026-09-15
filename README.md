# Python + AI Engineering Notes

My working notes on production Python and AI-agent engineering — written in my
own words while preparing for Python proficiency. Each chunk is small:
one concept, a plain-English explainer, a tiny runnable example, and the
interview "trap" question I want to be able to answer cold.

These are **learning notes**, not documentation. The goal is that I can explain
each one out loud in a discussion.

## How to use this repo

- Each folder is one concept **and one importable Python package** (e.g.
  `ch01_asyncio_and_gil`). Read the `README.md`; run or import the `example.py`.
- The template is deliberately the same for every chunk (below), so they stay
  small and comparable.
- I add and refine chunks over time — this is a living repo.

### Setup & run (uv)

```bash
uv sync                                   # install dev deps (pytest)
uv run python -m ch01_asyncio_and_gil     # run one chapter's demo
uv run pytest                             # run all chapter tests
```

Each new chapter is registered as a package under `[tool.hatch.build.targets.wheel]`
in `pyproject.toml`, and its tests live in `tests/test_<pkg>.py`.

## Chunk template

```markdown
# <Concept>

**One-liner:** the headline I'd say in an interview.

## The idea
3-5 lines, plain English, my own words.

## Why it matters
1-2 lines — when/why I reach for it.

## Example
See `example.py` (or an inline snippet).
```

## Chunks

### Python — language & concurrency
1. [asyncio & the GIL](ch01_asyncio_and_gil/) — I/O-bound vs CPU-bound, why one thread works
2. [Decorators](ch02_decorators/) — wrapping behavior: retry, timing, caching
3. [Generators](ch03_generators/) — lazy, one-at-a-time, streaming
4. [Context managers](ch04_context_managers/) — guaranteed setup/teardown
5. [Python traps](ch05_python_traps/) — mutable defaults, late-binding closures

### Data modeling
6. [Pydantic at the edges](ch06_pydantic_at_the_edges/) — validate untrusted input at the boundary
7. [TypedDict vs dataclass vs Pydantic](ch07_typeddict_vs_dataclass_vs_pydantic/) — which type when

### AI / agents
8. [RAG](ch08_rag/) — retrieval-augmented generation, end to end
9. [LLM fundamentals](ch09_llm_fundamentals/) — NN, transformer, embeddings, hallucination
10. [LangGraph vs LangChain](ch10_langgraph_vs_langchain/) — blocks vs orchestration
11. [Tool calling](ch11_tool_calling/) — how an LLM calls your functions
12. [MCP vs A2A](ch12_mcp_vs_a2a/) — agent-to-tools vs agent-to-agent

### Production engineering
13. [Resilience trio](ch13_resilience_trio/) — retry, timeout, circuit breaker
14. [Evals vs tests vs quality gate](ch14_evals_vs_tests_vs_gate/) — three layers
15. [Observability](ch15_observability/) — logs, metrics, traces
16. [REST statelessness](ch16_rest_statelessness/) — why it scales
