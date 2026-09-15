"""asyncio + Semaphore: fan out many I/O-bound calls, capped in-flight.

Run directly:   python -m ch01_asyncio_and_gil.example
Import + test:  from ch01_asyncio_and_gil import run_batch

Shows:
  1. gather fans out N coroutines and waits for all.
  2. A Semaphore caps how many run at once (backpressure).
  3. await asyncio.sleep yields to the loop; time.sleep would BLOCK it.
"""
from __future__ import annotations

import asyncio


async def fake_llm_call(n: int, sem: asyncio.Semaphore, delay: float = 0.05) -> str:
    """Pretend to call an LLM API. The sleep stands in for network wait.

    The Semaphore is an async context manager: `async with sem` acquires a slot
    on entry and releases it on exit, even if the body raises.
    """
    async with sem:
        await asyncio.sleep(delay)  # NON-blocking: loop runs other coroutines
        return f"answer-{n}"


async def run_batch(count: int, max_in_flight: int = 3, delay: float = 0.05) -> list[str]:
    """Run `count` fake calls, at most `max_in_flight` at a time, in input order."""
    sem = asyncio.Semaphore(max_in_flight)
    return await asyncio.gather(*[fake_llm_call(n, sem, delay) for n in range(count)])


def main() -> None:
    results = asyncio.run(run_batch(9))
    print(f"{len(results)} results:", results)


if __name__ == "__main__":
    main()
