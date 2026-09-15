"""Decorators: timing, configurable retry, and the async version.

Run directly:   python -m ch02_decorators.example
Import + test:  from ch02_decorators import retry, timed, async_retry

A decorator returns a `wrapper` that replaces the original function; the
original runs inside it via fn(*args, **kwargs).
"""
from __future__ import annotations

import asyncio
import time
from functools import wraps


def timed(fn):
    """Log how long a call took (a logging/timing concern)."""

    @wraps(fn)  # keep fn's name/docstring on the wrapper
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        wrapper.last_elapsed = time.perf_counter() - start  # exposed for tests
        return result

    return wrapper


def retry(attempts: int = 3, delay: float = 0.01):
    """Re-run on failure with exponential backoff. Configurable => extra layer."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for n in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if n == attempts - 1:  # last attempt -> give up
                        raise
                    time.sleep(delay * 2 ** n)  # exponential backoff

        return wrapper

    return decorator


def async_retry(attempts: int = 3, delay: float = 0.01):
    """Async retry: wrapper is async, awaits the call, uses asyncio.sleep."""

    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for n in range(attempts):
                try:
                    return await fn(*args, **kwargs)
                except Exception:
                    if n == attempts - 1:
                        raise
                    await asyncio.sleep(delay * 2 ** n)  # NON-blocking backoff

        return wrapper

    return decorator


def main() -> None:
    @timed
    def slow_add(a, b):
        time.sleep(0.05)
        return a + b

    print("slow_add:", slow_add(2, 3), f"({slow_add.last_elapsed:.3f}s)")


if __name__ == "__main__":
    main()
