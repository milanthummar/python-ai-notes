"""Context managers: guaranteed setup/teardown with `with`.

Run directly:   python -m ch04_context_managers
Import + test:  from ch04_context_managers import ManagedConnection, span, aspan

IMPLEMENT the class + two functions below so tests/test_ch04_context_managers.py
passes. The recurring point: teardown must run EVEN IF the body raises.
"""
from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from types import TracebackType
from typing import AsyncIterator, Iterator, Optional, Type


class ManagedConnection:
    """Class-based context manager simulating a resource (e.g. a DB connection).

    Implement `__enter__` and `__exit__`:
      - __enter__: set `is_open = True`, append "open" to `events`, return self.
      - __exit__:  set `is_open = False`, append "close" to `events` — ALWAYS,
                   even if the body raised. Return False so the exception
                   propagates (clean up, don't swallow).

    Example:
        conn = ManagedConnection()
        with conn as c:
            assert c.is_open is True
        assert conn.is_open is False
        assert conn.events == ["open", "close"]
    """

    def __init__(self) -> None:
        self.is_open = False
        self.events: list[str] = []

    def __enter__(self) -> "ManagedConnection":
        self.is_open = True
        self.events.append("open")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> bool:
        self.is_open = False
        self.events.append("close")
        return False


@contextmanager
def span(name: str, log: list[str]) -> Iterator[None]:
    """Generator-based context manager (a tracing 'span').

    Append f"start:{name}" on entry and f"end:{name}" on exit. The end MUST be
    guaranteed even if the body raises — wrap the `yield` in try/finally.

    Example:
        log = []
        with span("retrieve", log):
            log.append("body")
        assert log == ["start:retrieve", "body", "end:retrieve"]
    """
    log.append(f"start:{name}")
    try:
        yield
    finally:
        log.append(f"end:{name}")


@asynccontextmanager
async def aspan(name: str, log: list[str]) -> AsyncIterator[None]:
    """Async context manager — same behavior as `span`, but for `async with`.

    Append start/end around the yielded body, guaranteeing end via try/finally.

    Example:
        log = []
        async with aspan("llm", log):
            log.append("body")
        assert log == ["start:llm", "body", "end:llm"]
    """
    log.append(f"start:{name}")
    try:
        yield
    finally:
        log.append(f"end:{name}")

def main() -> None:
    log: list[str] = []
    with ManagedConnection() as conn:
        print("inside with, is_open:", conn.is_open)
    with span("retrieve", log):
        log.append("body")
    print("span log:", log)


if __name__ == "__main__":
    main()
