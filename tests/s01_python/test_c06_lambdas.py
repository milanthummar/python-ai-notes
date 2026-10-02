import pytest

from s01_python.c06_lambdas import apply_all, by_score, sort_by_name, sort_by_score, top_k

PAIRS = [("b", 0.2), ("c", 0.9), ("a", 0.5)]


def test_by_score_returns_the_score():
    assert by_score(("a", 0.5)) == 0.5


def test_by_score_matches_sort_by_score():
    assert sorted(PAIRS, key=by_score, reverse=True) == sort_by_score(PAIRS)


def test_sort_by_score_highest_first():
    assert sort_by_score(PAIRS) == [("c", 0.9), ("a", 0.5), ("b", 0.2)]


def test_sort_by_name():
    assert sort_by_name(PAIRS) == [("a", 0.5), ("b", 0.2), ("c", 0.9)]


def test_sorts_do_not_mutate_the_callers_list():
    pairs = list(PAIRS)

    sort_by_score(pairs)
    sort_by_name(pairs)

    assert pairs == [("b", 0.2), ("c", 0.9), ("a", 0.5)]


def test_sort_by_score_keeps_ties_in_original_order():
    tied = [("a", 0.5), ("b", 0.5)]

    assert sort_by_score(tied) == tied


def test_top_k_returns_the_best_pair():
    assert top_k(PAIRS, 1) == [("c", 0.9)]


def test_top_k_larger_than_the_list_returns_every_pair():
    assert top_k(PAIRS, 10) == [("c", 0.9), ("a", 0.5), ("b", 0.2)]


@pytest.mark.parametrize("k", [0, -1])
def test_top_k_rejects_non_positive_k(k):
    with pytest.raises(ValueError):
        top_k(PAIRS, k)


def test_apply_all_calls_each_function():
    assert apply_all([lambda n: n + 1, lambda n: n * 2], 10) == [11, 20]


def test_apply_all_empty():
    assert apply_all([], 10) == []
