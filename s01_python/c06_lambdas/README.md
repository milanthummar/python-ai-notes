# 1.6 Lambdas

**One-liner:** A lambda is a function with no name: `lambda args: expression`.
You pass it to something else, such as `sorted(..., key=...)`, instead of
writing a `def`.

## The idea

`lambda pair: pair[1]` is the same kind of object as a function defined with
`def`. It takes arguments and returns one expression. It cannot contain
statements (`if` blocks, `for`, `=`).

`sorted` does not know which part of a pair matters. `key` is a function it
calls once per item, and it compares whatever that function returns. `pair[0]`
is the text. `pair[1]` is the score. `reverse=True` puts the larger score
first.

`sorted` returns a new list and is stable: two items with the same key stay
in their original order. The late-binding trap (`lambda x: i * x` inside a
loop) is 1.5, not this chunk.

## Why it matters

`retrieve` in 3.1 sorts with `key=lambda pair: pair[1]`. The same shape shows
up anywhere you hand a small function to another function: a sort key, a
callback, a list of handlers.

## Spec

Standard library only. Implement in `s01_python/c06_lambdas/example.py`,
re-export the five functions from `__init__.py`, add `__main__.py`, and write
`tests/s01_python/test_c06_lambdas.py`.

```python
def by_score(pair: tuple[str, float]) -> float: ...

def sort_by_score(pairs: list[tuple[str, float]]) -> list[tuple[str, float]]: ...

def sort_by_name(pairs: list[tuple[str, float]]) -> list[tuple[str, float]]: ...

def top_k(pairs: list[tuple[str, float]], k: int) -> list[tuple[str, float]]: ...

def apply_all(fns: list[Callable[[int], int]], x: int) -> list[int]: ...
```

A pair is `(text, score)`, the same shape `retrieve` returns.

### `by_score`

- Return `pair[1]`, the score.
- This is the `def` form of `lambda pair: pair[1]`. A test will pass `by_score`
  itself as a `key` and compare it with `sort_by_score`.

### `sort_by_score`

- Return a new list, highest score first.
- The `key` must be a lambda: `lambda pair: pair[1]`.
- Do not mutate `pairs`.
- Equal scores keep their original order.

```python
sort_by_score([("b", 0.2), ("c", 0.9), ("a", 0.5)])
# [("c", 0.9), ("a", 0.5), ("b", 0.2)]
```

### `sort_by_name`

- Return a new list, sorted by the text (`pair[0]`) ascending.
- The `key` must be a lambda: `lambda pair: pair[0]`.
- Do not mutate `pairs`.
- Equal names keep their original order.

On the same input as above, name order and score order disagree:

```python
sort_by_name([("b", 0.2), ("c", 0.9), ("a", 0.5)])
# [("a", 0.5), ("b", 0.2), ("c", 0.9)]
```

### `top_k`

- `k <= 0` raises `ValueError`.
- Otherwise return the first `k` pairs of `sort_by_score(pairs)`.
- `k` larger than the list returns every pair, still sorted by score.
- Do not mutate `pairs`.

### `apply_all`

- Call each function in `fns` with `x`, in order, and return the list of
  results.
- `fns` may contain lambdas, `def` functions, or both. Treat them the same.
- An empty `fns` returns `[]`.

```python
apply_all([lambda n: n + 1, lambda n: n * 2], 10)  # [11, 20]
```

### `main()`

Build `[("b", 0.2), ("c", 0.9), ("a", 0.5)]`. Print `sort_by_score`,
`sort_by_name`, and `top_k(..., 1)`. Then print `apply_all` on two lambdas,
as in the example above, so a lambda is created in one place and called in
another.

### Tests you should write

| Test | Assert |
|---|---|
| `by_score` | `by_score(("a", 0.5)) == 0.5` |
| `by_score` matches the lambda | `sorted(pairs, key=by_score, reverse=True) == sort_by_score(pairs)` for the `("b", 0.2), ("c", 0.9), ("a", 0.5)` list |
| sort by score | that same list returns `[("c", 0.9), ("a", 0.5), ("b", 0.2)]` |
| sort by name | that same list returns `[("a", 0.5), ("b", 0.2), ("c", 0.9)]` |
| no mutation | after both sorts, the caller's list is still `[("b", 0.2), ("c", 0.9), ("a", 0.5)]` |
| stable score tie | `[("a", 0.5), ("b", 0.5)]` stays in that order after `sort_by_score` |
| `top_k` | `top_k(pairs, 1) == [("c", 0.9)]` |
| `top_k` too big | `k=10` returns all three pairs, score order |
| `top_k` bad k | `k=0` and `k=-1` raise `ValueError` |
| `apply_all` | `[lambda n: n + 1, lambda n: n * 2]` and `10` returns `[11, 20]` |
| `apply_all` empty | `apply_all([], 10) == []` |

## Interview trap

> Q: How is `lambda pair: pair[1]` different from `def by_score(pair): return pair[1]`?
> A: It isn't, at runtime. Both are functions. A lambda is only the one-expression form, used when the function is passed straight into something else.

> Q: What does `key` do in `sorted`?
> A: It is called once per item. `sorted` compares the returned values, not the items themselves. `reverse=True` flips that order. Equal keys keep their original order.
