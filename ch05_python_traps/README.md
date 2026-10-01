# Python traps

**One-liner:** Mutable default arguments are created once and shared across calls;
closures capture variables by name, so a loop variable is read later, not when
the function was created.

## The idea

Two bugs that look correct and fail only on the second call or the second
function.

- **Mutable default.** `def f(item, bucket=[])` builds `bucket` once, at
  function definition. Every call that omits `bucket` appends to that same
  list.
- **Late-binding closure.** `lambda x: i * x` inside `for i in ...` does not
  store the current `i`. It looks `i` up when the lambda *runs*, which is after
  the loop, so every lambda sees the final `i`.

Fixes: use `None` and create the list inside the function; bind the loop
variable as a default argument (`lambda x, i=i: i * x`), which is evaluated at
definition time.

## Why it matters

A shared default list silently leaks data between requests. A late-bound
closure makes every generated callback behave like the last one — easy to
ship, painful to debug.

## Spec

Implement these four functions in `ch05_python_traps/example.py` and re-export
them from `ch05_python_traps/__init__.py`. You write the tests in
`tests/test_ch05_python_traps.py`. Register `"ch05_python_traps"` in
`pyproject.toml` packages when the package exists.

```python
def buggy_append(item: str, bucket: list[str] = []) -> list[str]: ...

def safe_append(item: str, bucket: list[str] | None = None) -> list[str]: ...

def late_multipliers(n: int) -> list[Callable[[int], int]]: ...

def fixed_multipliers(n: int) -> list[Callable[[int], int]]: ...
```

### `buggy_append` — the trap, on purpose

- Append `item` to `bucket` and return that same list.
- The default `bucket` is one list for the life of the process.
- Two calls that omit `bucket` share it: `buggy_append("a")` then
  `buggy_append("b")` returns `["a", "b"]`, and both results are the **same
  object**.

### `safe_append` — the fix

- If `bucket` is `None`, start a new list. Never use a mutable default.
- Append `item` and return the list.
- Two calls that omit `bucket` are independent: `["a"]` then `["b"]`, and the
  results are **not** the same object.
- If the caller passes a list, mutate and return **that** object.

### `late_multipliers(n)` — the trap, on purpose

- Return `n` callables. The callable at index `i` is *meant* to compute
  `i * x`, but it is written so every callable reads `i` at call time.
- After `funcs = late_multipliers(3)`, **every** `funcs[k](10)` returns `20`
  (the final `i`, which is `2`).
- `late_multipliers(0)` returns `[]`.

### `fixed_multipliers(n)` — the fix

- Same shape, but each callable captures its own `i` at definition time.
- `fixed_multipliers(3)[0](10) == 0`, `[1](10) == 10`, `[2](10) == 20`.
- `fixed_multipliers(0)` returns `[]`.

`n` is assumed `>= 0`. Do not add other behavior.

### Tests you should write

Put the two `buggy_append` assertions in **one** test. The shared default list
lives for the whole process, so other tests must not call `buggy_append`
without an explicit list.

| Test | Assert |
|---|---|
| shared default | `first = buggy_append("a")`, `second = buggy_append("b")` → `second == ["a", "b"]` and `first is second` |
| safe calls are independent | `safe_append("a") == ["a"]`, `safe_append("b") == ["b"]`, and the two lists are not the same object |
| caller-owned list | `bucket = ["x"]`; `safe_append("y", bucket) is bucket` and `bucket == ["x", "y"]` |
| late binding | every `late_multipliers(3)[k](10) == 20` |
| fixed binding | `fixed_multipliers(3)[k](10) == k * 10` for `k` in `0, 1, 2` |
| empty | both multiplier functions return `[]` for `n == 0` |

## Interview trap

> Q: Why does `def f(items=[])` remember items from the last call?
> A: The default list is created once, when the function is defined, and reused.
> Use `items=None` and create a new list inside the function.

> Q: Why do all the lambdas in a loop return the last value?
> A: Closures look up the variable when they run, not when they were created.
> Bind it early: `lambda x, i=i: ...`.
