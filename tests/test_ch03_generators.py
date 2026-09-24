import inspect

from ch03_generators import first_grounded, lazy_batches, stream_tokens


def test_stream_tokens_yields_each_token():
    assert list(stream_tokens("reset your password")) == ["reset", "your", "password"]


def test_stream_tokens_empty_string():
    assert list(stream_tokens("")) == []


def test_stream_tokens_is_lazy_generator():
    # Calling it should return a generator, not a list — nothing produced yet.
    gen = stream_tokens("a b c")
    assert inspect.isgenerator(gen)
    assert next(gen) == "a"


def test_lazy_batches_splits_into_chunks():
    assert list(lazy_batches(["a", "b", "c", "d", "e"], 2)) == [
        ["a", "b"],
        ["c", "d"],
        ["e"],
    ]


def test_lazy_batches_exact_multiple():
    assert list(lazy_batches(["a", "b", "c", "d"], 2)) == [["a", "b"], ["c", "d"]]


def test_lazy_batches_is_generator():
    assert inspect.isgenerator(lazy_batches(["a", "b"], 1))


def test_first_grounded_returns_first_over_threshold():
    assert first_grounded([("a", 0.2), ("b", 0.9), ("c", 0.95)], 0.8) == "b"


def test_first_grounded_none_when_nothing_qualifies():
    assert first_grounded([("a", 0.1), ("b", 0.2)], 0.8) is None


def test_first_grounded_stops_early_and_does_not_consume_rest():
    # This generator records how many pairs it actually produced. Once a match
    # is found, first_grounded must stop pulling — so items after the match are
    # never produced.
    produced: list[str] = []

    def source():
        for passage, score in [("a", 0.2), ("b", 0.9), ("c", 0.99), ("d", 0.99)]:
            produced.append(passage)
            yield passage, score

    result = first_grounded(source(), 0.8)

    assert result == "b"
    # "a" and "b" were produced to find the match; "c"/"d" must NOT be.
    assert produced == ["a", "b"]
