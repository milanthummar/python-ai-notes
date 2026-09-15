"""asyncio + Semaphore: fan out many I/O-bound calls, capped in-flight.

Run: python example.py

Shows:
  1. gather fans out N coroutines and waits for all.
  2. A Semaphore caps how many run at once (backpressure).
  3. await asyncio.sleep yields to the loop; time.sleep would BLOCK it.
"""
import asyncio
import time


async def fake_llm_call(n: int, sem: asyncio.Semaphore) -> str:
    """Pretend to call an LLM API. The sleep stands in for network wait."""
    async with sem:  # acquire a slot on entry, release on exit (even on error)
        print(f"  start  #{n}")
        await asyncio.sleep(0.5)  # NON-blocking: the loop runs other coroutines
        print(f"  finish #{n}")
        return f"answer-{n}"


async def main() -> None:
    max_in_flight = 3
    sem = asyncio.Semaphore(max_in_flight)

    started = time.perf_counter()
    results = await asyncio.gather(*[fake_llm_call(n, sem) for n in range(9)])
    elapsed = time.perf_counter() - started

    # 9 calls, 0.5s each, 3 at a time => ~3 waves => ~1.5s, not 4.5s.
    print(f"\n{len(results)} results in {elapsed:.1f}s (capped at {max_in_flight} at once)")
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
