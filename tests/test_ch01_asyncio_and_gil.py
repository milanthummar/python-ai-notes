import asyncio
import time

from ch01_asyncio_and_gil import run_batch


async def test_run_batch_returns_all_results_in_order():
    results = await run_batch(count=5, max_in_flight=2, delay=0.01)

    assert results == [f"answer-{n}" for n in range(5)]


async def test_semaphore_serializes_when_cap_is_one():
    # With max_in_flight=1, three 0.05s calls run one-after-another (~0.15s),
    # proving the Semaphore actually caps concurrency.
    start = time.perf_counter()
    await run_batch(count=3, max_in_flight=1, delay=0.05)
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.15


async def test_high_cap_runs_concurrently():
    # With a cap >= count, all run together (~one delay, not the sum).
    start = time.perf_counter()
    await run_batch(count=5, max_in_flight=5, delay=0.05)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.15
