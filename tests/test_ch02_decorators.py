import pytest

from ch02_decorators import async_retry, retry, timed


def test_timed_preserves_result_and_records_elapsed():
    @timed
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    assert add.last_elapsed >= 0


def test_timed_keeps_function_metadata():
    @timed
    def named_fn():
        """docstring stays."""

    assert named_fn.__name__ == "named_fn"
    assert named_fn.__doc__ == "docstring stays."


def test_retry_succeeds_after_transient_failures():
    calls = {"n": 0}

    @retry(attempts=3, delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3


def test_retry_reraises_after_exhausting_attempts():
    @retry(attempts=2, delay=0)
    def always_fails():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        always_fails()


async def test_async_retry_succeeds_after_failure():
    calls = {"n": 0}

    @async_retry(attempts=3, delay=0)
    async def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("transient")
        return "ok"

    assert await flaky() == "ok"
    assert calls["n"] == 2
