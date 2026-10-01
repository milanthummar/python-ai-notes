from ch05_python_traps import (
    buggy_append,
    fixed_multiplier,
    late_multiplier,
    safe_append,
)


def test_buggy_append_shares_default_list():
    # The default list lives for the whole process, so both calls stay in this
    # one test and no other test calls buggy_append without a list.
    first = buggy_append("a")
    second = buggy_append("b")

    assert second == ["a", "b"]
    assert first is second


def test_safe_append_calls_are_independent():
    first = safe_append("a")
    second = safe_append("b")

    assert first == ["a"]
    assert second == ["b"]
    assert first is not second


def test_safe_append_mutates_caller_list():
    bucket = ["x"]

    result = safe_append("y", bucket)

    assert result is bucket
    assert bucket == ["x", "y"]


def test_late_multiplier_every_function_uses_last_i():
    funcs = late_multiplier(3)

    assert [fn(10) for fn in funcs] == [20, 20, 20]


def test_fixed_multiplier_each_function_keeps_its_i():
    funcs = fixed_multiplier(3)

    assert [fn(10) for fn in funcs] == [0, 10, 20]


def test_multipliers_empty_for_zero():
    assert late_multiplier(0) == []
    assert fixed_multiplier(0) == []
