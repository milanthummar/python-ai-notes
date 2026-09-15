# asyncio & the GIL

**One-liner:** For I/O-bound work I use asyncio — one thread overlapping the
waits — because the GIL rules out real thread parallelism anyway; for CPU-bound
work I use multiprocessing.

## The idea

The **GIL** (Global Interpreter Lock) lets only one thread run Python bytecode
at a time. It's released while a thread waits on I/O. So:

- **asyncio** — one thread, coroutines take turns at `await`. While one request
  waits on the network/LLM, the event loop runs another. Great for I/O-bound work.
- **threads** — real OS threads, but the GIL serialises them: concurrency for
  I/O, but no CPU parallelism.
- **multiprocessing** — separate processes, each with its own GIL, so they run
  truly in parallel across cores. This is the tool for CPU-bound work.

Concurrency = tasks taking turns. Parallelism = multiple cores at the same instant.

## Why it matters

Batching thousands of LLM calls is I/O-bound (waiting on the API), so asyncio
overlaps the waits cheaply. A `Semaphore` caps how many run at once so I don't
stampede the API or blow the cost budget.

## Example

See `example.py` — fans out N fake "LLM calls" with `gather`, capped by a
`Semaphore`, and shows why `await asyncio.sleep` (not `time.sleep`) is required.

## Interview trap

> Q: What happens if you put `time.sleep()` inside a coroutine?
> A: It **blocks the event loop** — it holds the single thread, so no other
> coroutine can run until it returns. Use `await asyncio.sleep()`, which yields
> control back to the loop.

> Q: 10,000 LLM calls — threads or asyncio?
> A: asyncio. The work is I/O-bound, so I overlap the waits in one thread. The
> GIL limits threads and they cost more memory. I'd cap concurrency with a
> Semaphore.
