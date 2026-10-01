# 1.4 Context managers

**One-liner:** A context manager guarantees setup and teardown around a block —
`with` runs the cleanup even if the body raises, so I don't hand-roll
try/finally for every resource.

## The idea

`with` gives a resource a guaranteed lifecycle: acquire on entry, release on
exit — **even on an exception or early return**. Without it you'd need a manual
`try/finally` around every DB connection, file, or lock.

Two ways to write one:

- **Class-based** — define `__enter__` (setup, returns the resource) and
  `__exit__` (teardown, always runs). `__exit__` returning `True` *suppresses*
  the exception; return `False`/`None` to let it propagate.
- **`@contextmanager`** — a generator: everything before `yield` is setup,
  everything after is teardown. Wrap the `yield` in `try/finally` so teardown
  runs on error.

Async resources use `async with` (`__aenter__`/`__aexit__`, or
`@asynccontextmanager`).

## Why it matters

- **Resource safety** — DB connections, files, and locks get released even when
  the body throws, so nothing leaks.
- **Observability spans** — wrap an agent step in a context manager that records
  start/end (and duration); the "end" is guaranteed, so a failing step still
  closes its span cleanly.
- **Async gates** — an `asyncio.Semaphore` is itself an async context manager:
  `async with sem` acquires on entry, releases on exit even on error.

## Example

See `example.py`:

- `ManagedConnection` — class-based CM; opens on enter, closes on exit **even if
  the body raises**, and lets the exception propagate.
- `span` — `@contextmanager` (generator) tracing span using `try/finally`.
- `aspan` — the `@asynccontextmanager` async version for `async with`.

## Interview trap

> Q: What happens if `__exit__` returns `True`?
> A: It **suppresses** the exception — the `with` block swallows it. Usually you
> want `False`/`None` so errors propagate; you clean up, you don't hide the bug.

> Q: Why `try/finally` inside a `@contextmanager` generator?
> A: So the code after `yield` (teardown) still runs if the body raises.
> Without `finally`, an exception skips your cleanup.

> Q: How do you clean up an async resource?
> A: `async with` + `__aenter__`/`__aexit__` (or `@asynccontextmanager`). Same
> guarantee, awaitable setup/teardown.
