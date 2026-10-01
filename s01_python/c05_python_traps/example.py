"""Python traps: mutable default arguments and late-binding closures.

Run directly:   python -m s01_python.c05_python_traps
Import + test:  from s01_python.c05_python_traps import buggy_append, safe_append

Each trap has a buggy version (kept on purpose) and its fix.
"""
from collections.abc import Callable


def buggy_append(item: str, bucket: list[str] = []) -> list[str]:
    """Append `item` to `bucket` and return it. Buggy on purpose.

    The default list is created once, when the function is defined, so every
    call that omits `bucket` appends to the same list.

    Example:
        first = buggy_append("a")   # ["a"]
        second = buggy_append("b")  # ["a", "b"], and first is second
    """
    bucket.append(item)
    return bucket


def safe_append(item: str, bucket: list[str] | None = None) -> list[str]:
    """Append `item` to `bucket` and return it, without a shared default.

    A new list is created on every call that omits `bucket`. A list passed by
    the caller is mutated and returned as the same object.

    Example:
        safe_append("a")  # ["a"]
        safe_append("b")  # ["b"]
    """
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


def late_multiplier(n: int) -> list[Callable[[int], int]]:
    """Return `n` functions meant to compute `i * x`. Buggy on purpose.

    Each lambda reads the loop variable `i` when it is called, not when it was
    created, so every function uses the final `i` (`n - 1`).

    Example:
        [fn(10) for fn in late_multiplier(3)]  # [20, 20, 20]
    """
    func = []
    for i in range(n):
        func.append(lambda x: x * i)
    return func


def fixed_multiplier(n: int) -> list[Callable[[int], int]]:
    """Return `n` functions where function `i` computes `i * x`.

    `i=i` stores the current loop value as a default argument, which is
    evaluated when the lambda is created, so each function keeps its own `i`.

    Example:
        [fn(10) for fn in fixed_multiplier(3)]  # [0, 10, 20]
    """
    func = []
    for i in range(n):
        func.append(lambda x, i=i: x * i)
    return func


def main() -> None:
    print("buggy: ", buggy_append("a"), buggy_append("b"))
    print("safe:  ", safe_append("a"), safe_append("b"))

    late = late_multiplier(3)
    fixed = fixed_multiplier(3)
    print("late:  ", [fn(10) for fn in late])
    print("fixed: ", [fn(10) for fn in fixed])


if __name__ == "__main__":
    main()
