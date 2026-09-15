"""Decorators: timing, configurable retry, and the async version.

Run: python example.py

A decorator returns a `wrapper` that replaces the original function; the
original runs inside it via fn(*args, **kwargs).
"""
import asyncio
import time
from functools import wraps


# 1) @timed — measure how long a call took (a logging/timing concern).
def timed(fn):
    @wraps(fn)  # keep fn's name/docstring on the wrapper
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"  {fn.__name__} took {time.perf_counter() - start:.3f}s")
        return result

    return wrapper


@timed
def slow_add(a, b):
    time.sleep(0.1)
    return a + b


# 2) @retry(...) — CONFIGURABLE: takes args, so it has one extra layer.
def retry(attempts=3, delay=0.05):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for n in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if n == attempts - 1:  # last attempt -> give up
                        raise
                    print(f"  attempt {n + 1} failed ({e}); retrying...")
                    time.sleep(delay * 2 ** n)  # exponential backoff

        return wrapper

    return decorator


_calls = {"n": 0}


@retry(attempts=3)
def flaky():
    _calls["n"] += 1
    if _calls["n"] < 3:
        raise ValueError("blip")
    return "ok on attempt 3"


# 3) ASYNC retry — wrapper is async, awaits the call, uses asyncio.sleep.
def async_retry(attempts=3, delay=0.01):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for n in range(attempts):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if n == attempts - 1:
                        raise
                    print(f"  async attempt {n + 1} failed ({e}); retrying...")
                    await asyncio.sleep(delay * 2 ** n)  # NON-blocking

        return wrapper

    return decorator


_acalls = {"n": 0}


@async_retry(attempts=3)
async def flaky_llm(prompt):
    _acalls["n"] += 1
    if _acalls["n"] < 2:
        raise ConnectionError("timeout")
    return f"answer: {prompt}"


def main():
    print("timed:", slow_add(2, 3))
    print("retry:", flaky())
    print("async_retry:", asyncio.run(flaky_llm("hi")))


if __name__ == "__main__":
    main()
