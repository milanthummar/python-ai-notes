import pytest

from s03_ai_agents.c01_rag import (
    build_prompt,
    chunk_text,
    cosine,
    embed,
    retrieve,
    tokenize,
)


def test_chunk_windows():
    words = " ".join(f"w{i}" for i in range(1, 11))

    assert chunk_text(words, size=4, overlap=1) == [
        "w1 w2 w3 w4",
        "w4 w5 w6 w7",
        "w7 w8 w9 w10",
    ]


def test_chunk_short_text():
    assert chunk_text("a b c", size=50, overlap=10) == ["a b c"]


@pytest.mark.parametrize("text", ["", "   "])
def test_chunk_empty(text):
    assert chunk_text(text, size=4, overlap=1) == []


@pytest.mark.parametrize(
    ("size", "overlap"),
    [
        (0, 0),
        (4, -1),
        (4, 4),
    ],
)
def test_chunk_bad_args(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("a b c", size, overlap)


def test_tokenize_keeps_letters_and_digits():
    assert tokenize("Reset, PASSWORD!") == ["reset", "password"]


def test_cosine_identical_text():
    vector = embed("the cat sat")

    assert cosine(vector, vector) == pytest.approx(1.0)


def test_cosine_disjoint_or_empty():
    assert cosine(embed("cat"), embed("dog")) == 0.0
    assert cosine(embed(""), embed("cat")) == 0.0


def test_retrieve_ranks_best_match_first():
    chunks = [
        "dogs chase balls",
        "the cat sat on the mat",
        "a cat sat quietly",
    ]

    results = retrieve("cat sat", chunks, k=2)

    assert [chunk for chunk, _ in results] == [
        "a cat sat quietly",
        "the cat sat on the mat",
    ]
    assert results[0][1] > results[1][1]


def test_retrieve_drops_unrelated_chunks():
    results = retrieve(
        "cat sat",
        ["dogs chase balls", "birds fly", "a cat sat quietly"],
        k=3,
    )

    assert [chunk for chunk, _ in results] == ["a cat sat quietly"]


def test_retrieve_returns_at_most_k():
    chunks = ["cat sat here", "cat sat quietly", "the cat sat down"]

    assert len(retrieve("cat sat", chunks, k=2)) == 2


@pytest.mark.parametrize("k", [0, -1])
def test_retrieve_rejects_non_positive_k(k):
    with pytest.raises(ValueError):
        retrieve("cat sat", ["cat sat"], k=k)


def test_retrieve_keeps_original_order_on_ties():
    chunks = ["alpha cat", "beta cat"]

    results = retrieve("cat", chunks, k=2)

    assert [chunk for chunk, _ in results] == chunks
    assert results[0][1] == pytest.approx(results[1][1])


def test_prompt_numbers_contexts_from_one():
    prompt = build_prompt(
        "where did the cat sit",
        ["a cat sat quietly", "the cat sat on the mat"],
    )
    lines = prompt.splitlines()

    assert "[1] a cat sat quietly" in lines
    assert "[2] the cat sat on the mat" in lines
    assert lines[-1] == "Question: where did the cat sit"


def test_prompt_no_context_uses_none():
    lines = build_prompt("where did the cat sit", []).splitlines()

    assert "(none)" in lines
    assert lines[-1] == "Question: where did the cat sit"
