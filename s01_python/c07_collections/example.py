from collections import Counter, defaultdict, deque


def tally(words: list[str]) -> list[tuple[str, int]]:
    return Counter(words).most_common()


def group_ids(rows: list[tuple[str, int]]) -> dict[str, list[int]]:
    groups = defaultdict(list)
    for key, value in rows:
        groups[key].append(value)
    return dict(groups)


class RecentItems:

    def __init__(self, limit: int) -> None:
        if limit <= 0:
            raise ValueError("limit must be positive")

        self._limit = limit
        self._items_list = deque(maxlen=limit)

    def add(self, item: str) -> None:
        self._items_list.append(item)

    def items(self) -> list[str]:
        return list(self._items_list)


def main():
    example_set_for_tally = ["cat", "dog", "cat", "bird", "dog"]
    example_tuple_for_group_ids = [("kb", 1), ("web", 2), ("kb", 3)]

    print("tally ->")
    print(tally(example_set_for_tally))
    print("group_ids ->")
    print(group_ids(example_tuple_for_group_ids))
    print("Recent Items ->")
    recent_items = RecentItems(2)
    recent_items.add("a")
    recent_items.add("b")
    recent_items.add("c")
    print(recent_items.items())

if __name__== "__main__":
    main()