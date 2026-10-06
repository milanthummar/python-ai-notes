import pytest

from s01_python.c07_collections import RecentItems, group_ids, tally


def test_tally_orders_by_count_then_first_seen():
    assert tally(["cat", "dog", "cat", "bird", "dog"]) == [
        ("cat", 2),
        ("dog", 2),
        ("bird", 1),
    ]


def test_tally_empty():
    assert tally([]) == []


def test_group_ids_one_name():
    assert group_ids([("kb", 1), ("kb", 3)]) == {"kb": [1, 3]}


def test_group_ids_two_names():
    grouped = group_ids([("kb", 1), ("web", 2), ("kb", 3)])

    assert grouped == {"kb": [1, 3], "web": [2]}
    assert type(grouped) is dict


def test_group_ids_lists_are_distinct():
    grouped = group_ids([("kb", 1), ("web", 2)])

    assert grouped["kb"] is not grouped["web"]


def test_group_ids_empty():
    assert group_ids([]) == {}


def test_recent_items_drops_the_oldest():
    recent = RecentItems(2)
    recent.add("a")
    recent.add("b")
    recent.add("c")

    assert recent.items() == ["b", "c"]


def test_recent_items_under_the_cap():
    recent = RecentItems(3)
    recent.add("a")
    recent.add("b")

    assert recent.items() == ["a", "b"]


@pytest.mark.parametrize("limit", [0, -1])
def test_recent_items_rejects_non_positive_limit(limit):
    with pytest.raises(ValueError):
        RecentItems(limit)


def test_recent_items_instances_do_not_share_storage():
    first = RecentItems(2)
    second = RecentItems(2)
    first.add("a")

    assert first.items() == ["a"]
    assert second.items() == []
