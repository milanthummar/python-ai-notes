# 1.7 Collections

**One-liner:** `Counter` counts, `defaultdict` fills in a missing key, and
`deque` keeps a fixed window. Each one replaces a loop that is easy to get wrong.

## The idea

- **`Counter`** is a dict from item to count. `most_common()` lists pairs
  highest count first. Equal counts stay in the order the item was first seen.
- **`defaultdict(list)`** creates a new empty list the first time a key is
  used. Each key gets its own list. This is the same trap as 1.5 if you
  instead reuse one list as the default.
- **`deque(maxlen=n)`** is a queue with a cap. `append` adds on the right.
  Once it holds `n` items, the oldest item on the left is dropped.

## Why it matters

RAG counts tokens with `Counter`. Grouping retrieved rows by source is
`defaultdict`. A bounded chat history is `deque(maxlen=...)`. The same three
tools show up in interview problems. Practice those problems on LeetCode.
This chunk only teaches the tools.

## Spec

Standard library only. Implement in `s01_python/c07_collections/example.py`,
re-export `tally`, `group_ids`, and `RecentItems` from `__init__.py`, add
`__main__.py`, and write `tests/s01_python/test_c07_collections.py`.

```python
def tally(words: list[str]) -> list[tuple[str, int]]: ...

def group_ids(rows: list[tuple[str, int]]) -> dict[str, list[int]]: ...

class RecentItems:
    def __init__(self, limit: int) -> None: ...
    def add(self, item: str) -> None: ...
    def items(self) -> list[str]: ...
```

### `tally`

- Count with `Counter`.
- Return `most_common()`: `(word, count)` pairs, highest count first.
- Equal counts stay in first-seen order.
- An empty list returns `[]`.

```python
tally(["cat", "dog", "cat", "bird", "dog"])
# [("cat", 2), ("dog", 2), ("bird", 1)]
```

`"cat"` comes before `"dog"` because both have count 2 and `"cat"` appeared first.

### `group_ids`

- `rows` is a list of `(name, id)` pairs.
- Group the ids under each name, in the order they appeared.
- Use `defaultdict(list)`. Return a plain `dict`.
- A name that appears once still maps to a one-element list.
- An empty list returns `{}`.
- Two names must not share the same list object.

```python
group_ids([("kb", 1), ("web", 2), ("kb", 3)])
# {"kb": [1, 3], "web": [2]}
```

### `RecentItems`

- `limit <= 0` raises `ValueError`.
- `add` appends on the right.
- `items` returns the current items, oldest first.
- When the window is full, the next `add` drops the oldest item.
- Two instances do not share storage.

```python
recent = RecentItems(2)
recent.add("a")
recent.add("b")
recent.add("c")
recent.items()  # ["b", "c"]
```

### `main()`

Print `tally(["cat", "dog", "cat", "bird", "dog"])`, the `group_ids` example
above, and a `RecentItems(2)` after adding `"a"`, `"b"`, and `"c"`.

### Tests you should write

| Test | Assert |
|---|---|
| tally order | `["cat", "dog", "cat", "bird", "dog"]` → `[("cat", 2), ("dog", 2), ("bird", 1)]` |
| tally empty | `tally([]) == []` |
| group one name | `[("kb", 1), ("kb", 3)]` → `{"kb": [1, 3]}` |
| group two names | `[("kb", 1), ("web", 2), ("kb", 3)]` → `{"kb": [1, 3], "web": [2]}` |
| group lists are distinct | the lists for `"kb"` and `"web"` are not the same object |
| group empty | `group_ids([]) == {}` |
| recent window | `limit=2`, add `"a"`, `"b"`, `"c"` → `["b", "c"]` |
| recent under the cap | `limit=3`, add `"a"`, `"b"` → `["a", "b"]` |
| recent bad limit | `limit=0` and `limit=-1` raise `ValueError` |
| recent instances | two `RecentItems(2)` do not share items after adding to one of them |

## Interview trap

> Q: Why `defaultdict(list)` and not `groups = {}` with `groups[key] = []` once at the top?
> A: You do not know the keys ahead of time. `defaultdict(list)` builds a new list on the first use of each key. One shared list would mix every group together.

> Q: Why a `deque` for the last `n` items, not a list you slice?
> A: `append` and dropping the left end are cheap on a `deque`. A list pays to shift every item when you delete index 0.
