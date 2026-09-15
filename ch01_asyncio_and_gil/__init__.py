"""Chapter 01 — asyncio & the GIL.

Exposes the batching demo as importable functions so tests can call them.
"""

from ch01_asyncio_and_gil.example import fake_llm_call, run_batch

__all__ = ["fake_llm_call", "run_batch"]
