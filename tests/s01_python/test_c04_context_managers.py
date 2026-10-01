import pytest

from s01_python.c04_context_managers import ManagedConnection, aspan, span


class TestManagedConnection:
    def test_opens_and_closes(self):
        conn = ManagedConnection()
        with conn as c:
            assert c is conn
            assert c.is_open is True
        assert conn.is_open is False
        assert conn.events == ["open", "close"]

    def test_closes_even_when_body_raises(self):
        conn = ManagedConnection()
        with pytest.raises(ValueError):
            with conn:
                assert conn.is_open is True
                raise ValueError("boom")
        # teardown must have run despite the exception
        assert conn.is_open is False
        assert conn.events == ["open", "close"]


def test_span_records_start_body_end_in_order():
    log: list[str] = []
    with span("retrieve", log):
        log.append("body")
    assert log == ["start:retrieve", "body", "end:retrieve"]


def test_span_end_runs_even_when_body_raises():
    log: list[str] = []
    with pytest.raises(RuntimeError):
        with span("retrieve", log):
            raise RuntimeError("fail")
    # the "end" must still be recorded (try/finally)
    assert log == ["start:retrieve", "end:retrieve"]


async def test_aspan_records_start_body_end_in_order():
    log: list[str] = []
    async with aspan("llm", log):
        log.append("body")
    assert log == ["start:llm", "body", "end:llm"]


async def test_aspan_end_runs_even_when_body_raises():
    log: list[str] = []
    with pytest.raises(RuntimeError):
        async with aspan("llm", log):
            raise RuntimeError("fail")
    assert log == ["start:llm", "end:llm"]
