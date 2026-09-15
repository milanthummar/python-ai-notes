# Python + AI Engineering Notes

My working notes on production Python and AI-agent engineering — written in my
own words while preparing for (and after) an SDE interview. Each chunk is small:
one concept, a plain-English explainer, a tiny runnable example, and the
interview "trap" question I want to be able to answer cold.

These are **learning notes**, not documentation. The goal is that I can explain
each one out loud in a discussion.

## How to use this repo

- Each folder is one concept. Read the `README.md`; run the `example.py`.
- The template is deliberately the same for every chunk (below), so they stay
  small and comparable.
- I add and refine chunks over time — this is a living repo.

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

## Interview trap
> Q: the likely gotcha
> A: the crisp answer
```

## Chunks

### Python — language & concurrency
1. [asyncio & the GIL](01-asyncio-and-gil/) — I/O-bound vs CPU-bound, why one thread works
2. [Decorators](02-decorators/) — wrapping behavior: retry, timing, caching
3. [Generators](03-generators/) — lazy, one-at-a-time, streaming
4. [Context managers](04-context-managers/) — guaranteed setup/teardown
5. [Python traps](05-python-traps/) — mutable defaults, late-binding closures

### Data modeling
6. [Pydantic at the edges](06-pydantic-at-the-edges/) — validate untrusted input at the boundary
7. [TypedDict vs dataclass vs Pydantic](07-typeddict-vs-dataclass-vs-pydantic/) — which type when

### AI / agents
8. [RAG](08-rag/) — retrieval-augmented generation, end to end
9. [LLM fundamentals](09-llm-fundamentals/) — NN, transformer, embeddings, hallucination
10. [LangGraph vs LangChain](10-langgraph-vs-langchain/) — blocks vs orchestration
11. [Tool calling](11-tool-calling/) — how an LLM calls your functions
12. [MCP vs A2A](12-mcp-vs-a2a/) — agent-to-tools vs agent-to-agent

### Production engineering
13. [Resilience trio](13-resilience-trio/) — retry, timeout, circuit breaker
14. [Evals vs tests vs quality gate](14-evals-vs-tests-vs-gate/) — three layers
15. [Observability](15-observability/) — logs, metrics, traces
16. [REST statelessness](16-rest-statelessness/) — why it scales

## Origin

Distilled from a small mock "self-help agent" lab (LangGraph + Pydantic +
asyncio + evals + an MCP-shaped dispatcher). The lab proved the concepts; these
notes explain them.
