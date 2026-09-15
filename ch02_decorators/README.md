# Decorators

**One-liner:** A decorator is a function that wraps another function to add
behavior — retry, timing, caching, auth — without touching the original's body.

## The idea

`@my_decorator` above a function is just sugar for `fn = my_decorator(fn)`. The
decorator returns a `wrapper` that runs something before/after and calls the
original inside. `@wraps(fn)` keeps the original's name and docstring.

- **Configurable decorator** (`@retry(attempts=3)`) has one extra layer: the
  outer function takes the args and returns the real decorator.
- **Async decorator**: the wrapper must be `async` and must `await fn(...)`, and
  must use `await asyncio.sleep`, never `time.sleep` (which blocks the loop).

Java analogy: like an annotation backed by an interceptor / AOP aspect
(`@Transactional`, `@Cacheable`).

## Why it matters

Cross-cutting concerns (retry, logging/timing, caching, auth checks) repeat
across many functions. A decorator writes that logic **once** instead of
copy-pasting it into every function body.

## Example

See `example.py` — a `@timed` decorator, a configurable `@retry`, and the async
version used for a flaky "LLM" call.

## Interview trap

> Q: What in an LLM agent would you decorate, and why not inline the code?
> A: A `@retry` on the LLM/API call — the retry+backoff logic lives in one place
> instead of being repeated in every tool. Same for timing and caching.

> Q: Difference between the sync and async retry decorator?
> A: Same logic, but the async wrapper is `async` and `await`s the call, and uses
> `await asyncio.sleep` for the backoff — a `time.sleep` there would block the
> whole event loop.
