# 1.3 Generators

**One-liner:** A generator produces values lazily, one at a time with `yield`,
so I can stream results and stop early instead of building a whole list in
memory up front.

## The idea

A normal function `return`s once. A **generator** uses `yield` to hand back one
value and *pause*, resuming where it left off on the next `next()` call. Nothing
is computed until you ask for it (lazy), and only what you consume is produced.

- **Lazy** — values are generated on demand, not all at once.
- **Constant memory** — you hold one item at a time, not the whole sequence.
- **Early exit** — the caller can stop consuming whenever it's satisfied, so the
  generator never does the remaining work.

`list` builds and holds everything immediately; a generator streams it.

## Why it matters

Two direct payoffs for an agent:

- **Token streaming** — an LLM emits tokens one at a time; a generator lets me
  surface each token as it arrives instead of waiting for the full answer.
- **Stop when grounded** — when scanning retrieved passages for a good match, I
  can stop at the first one that clears the bar and never score the rest — no
  wasted compute or tokens.

## Example

See `example.py`:

- `stream_tokens` — yields tokens one at a time (streaming analogy).
- `lazy_batches` — yields fixed-size batches lazily (paging / RAG chunking).
- `first_grounded` — scans scored passages and returns the first above a
  threshold **without consuming the rest** (early termination).

## Interview trap

> Q: What's the difference between `return [x for x in xs]` and
> `(x for x in xs)`?
> A: The first builds the whole list in memory now. The second is a **generator
> expression** — lazy, one item at a time, constant memory.

> Q: Why use a generator for an LLM instead of a list?
> A: Streaming and early exit. I can process tokens as they arrive and stop as
> soon as I have a grounded answer, so I never compute or pay for the items I
> don't need.

> Q: Can you iterate a generator twice?
> A: No — it's exhausted after one pass. Re-create it (or use a list) if you
> need to iterate again.
