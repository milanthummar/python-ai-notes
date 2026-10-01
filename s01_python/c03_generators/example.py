"""Generators: lazy, one-at-a-time values with `yield`.

Run directly:   python -m s01_python.c03_generators
Import + test:  from s01_python.c03_generators import stream_tokens, lazy_batches, first_grounded

IMPLEMENT the three functions below so the tests in
tests/s01_python/test_c03_generators.py pass. Each must be a GENERATOR (use `yield`)
except `first_grounded`, which CONSUMES a generator and returns early.
"""
from __future__ import annotations

from typing import Iterable, Iterator, Optional


def stream_tokens(text: str) -> Iterator[str]:
    """Yield the whitespace-separated tokens of `text` one at a time.

    Simulates an LLM streaming its answer token by token: the caller can handle
    each token as it arrives instead of waiting for the whole string.

    Example:
        list(stream_tokens("reset your password")) == ["reset", "your", "password"]
        list(stream_tokens("")) == []

    Must be lazy — a generator, not a list.
    """
    for token in text.split():
        yield token


def lazy_batches(items: Iterable[str], size: int) -> Iterator[list[str]]:
    """Yield successive `size`-length batches (lists) from `items`, lazily.

    Like paging through data or chunking a document for RAG. The final batch may
    be shorter. `size` is assumed >= 1.

    Example:
        list(lazy_batches(["a", "b", "c", "d", "e"], 2))
            == [["a", "b"], ["c", "d"], ["e"]]

    Must yield each batch as it's built (don't materialise all batches first).
    """
    batch: list[str] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []

    if batch:
        yield batch


def first_grounded(
    scored: Iterable[tuple[str, float]], threshold: float
) -> Optional[str]:
    """Return the FIRST passage whose score >= threshold, or None if none do.

    `scored` is an iterable of (passage, score) pairs. Consume it lazily and
    stop as soon as a qualifying passage is found — do NOT keep pulling items
    after that (this is the early-termination point: the generator never
    produces the passages you didn't need).

    Example:
        first_grounded([("a", 0.2), ("b", 0.9), ("c", 0.95)], 0.8) == "b"
        first_grounded([("a", 0.1), ("b", 0.2)], 0.8) is None
    """
    for passage, score in scored:
        if score >= threshold:
            return passage
    return None


def main() -> None:
    print("tokens:", list(stream_tokens("reset your password")))
    print("batches:", list(lazy_batches(["a", "b", "c", "d", "e"], 2)))
    print("first grounded:", first_grounded([("a", 0.2), ("b", 0.9)], 0.8))


if __name__ == "__main__":
    main()
