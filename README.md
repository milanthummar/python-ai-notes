# Python + AI Engineering Notes

My working notes on production Python and AI-agent engineering — written in my
own words while preparing for Python proficiency. Each chunk is small:
one concept, a plain-English explainer, a tiny runnable example, and the
interview "trap" question I want to be able to answer cold.

These are **learning notes**, not documentation. The goal is that I can explain
each one out loud in a discussion.

## How to use this repo

- Chunks are grouped into numbered **sections**. Each section is a folder
  (`s01_python/`), and each chunk inside it is one concept **and one importable
  Python package** (`s01_python/c01_asyncio_and_gil/`). Read the chunk's
  `README.md`; run or import its `example.py`.
- Numbering is `section.chunk`: `s01_python/c01_asyncio_and_gil` is **1.1**.
- The template is deliberately the same for every chunk (below), so they stay
  small and comparable.
- I add and refine chunks over time — this is a living repo.

### Setup & run (uv)

```bash
uv sync                                             # install deps
uv run python -m s01_python.c01_asyncio_and_gil     # run one chunk's demo
uv run pytest                                       # run all tests
uv run pytest tests/s01_python                      # run one section's tests
```

### Adding a chunk

1. Create the next `cNN_<name>/` in its section, with `__init__.py`,
   `__main__.py`, `example.py` and `README.md` (heading `# <s>.<c> <Concept>`).
2. Put its tests in `tests/sNN_<section>/test_cNN_<name>.py`.
3. Add it to the section `README.md` and the index below.

A new section is a new `sNN_<name>/` folder with an `__init__.py`, listed under
`[tool.hatch.build.targets.wheel] packages` in `pyproject.toml`. Chunks inside
it need no registration.

Never renumber a published chunk; append new ones to the end of their section.

## Chunk template

```markdown
# <s>.<c> <Concept>

**One-liner:** the headline I'd say in an interview.

## The idea
3-5 lines, plain English, my own words.

## Why it matters
1-2 lines — when/why I reach for it.

## Example
See `example.py` (or an inline snippet).
```

## Chunks

Linked chunks have at least a spec; the rest are planned.

1. [Python — language & concurrency](s01_python/)
   1. [asyncio & the GIL](s01_python/c01_asyncio_and_gil/) — I/O-bound vs CPU-bound, why one thread works
   2. [Decorators](s01_python/c02_decorators/) — wrapping behavior: retry, timing, caching
   3. [Generators](s01_python/c03_generators/) — lazy, one-at-a-time, streaming
   4. [Context managers](s01_python/c04_context_managers/) — guaranteed setup/teardown
   5. [Python traps](s01_python/c05_python_traps/) — mutable defaults, late-binding closures
   6. [Lambdas](s01_python/c06_lambdas/) — one-expression functions, and `key` for `sorted`
2. [Data modeling](s02_data_modeling/)
   1. [Pydantic at the edges](s02_data_modeling/c01_pydantic_at_the_edges/) — validate untrusted input at the boundary
   2. [TypedDict vs dataclass vs Pydantic](s02_data_modeling/c02_typeddict_vs_dataclass_vs_pydantic/) — which type when
3. [AI / agents](s03_ai_agents/)
   1. [RAG](s03_ai_agents/c01_rag/) — chunk, embed, retrieve, build the prompt
   2. [LLM fundamentals](s03_ai_agents/c02_llm_fundamentals/) — logits, softmax, temperature, hallucination
   3. [LangGraph vs LangChain](s03_ai_agents/c03_langgraph_vs_langchain/) — state graph vs chain
   4. [Tool calling](s03_ai_agents/c04_tool_calling/) — how an LLM calls your functions
   5. [MCP vs A2A](s03_ai_agents/c05_mcp_vs_a2a/) — agent-to-tools vs agent-to-agent
4. Production engineering
   1. Resilience trio — retry, timeout, circuit breaker
   2. Evals vs tests vs quality gate — three layers
   3. Observability — logs, metrics, traces
   4. REST statelessness — why it scales
