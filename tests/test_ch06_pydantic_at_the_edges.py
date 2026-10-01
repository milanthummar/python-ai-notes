import pytest
from pydantic import ValidationError

from ch06_pydantic_at_the_edges import AnswerArgs, LookupArgs


def test_lookup_strips_then_accepts_known_intent():
    args = LookupArgs(intent=" access ")

    assert args.intent == "access"


@pytest.mark.parametrize("intent", ["", "   "])
def test_lookup_rejects_empty_intent(intent):
    with pytest.raises(ValidationError):
        LookupArgs(intent=intent)


def test_lookup_rejects_unknown_intent():
    with pytest.raises(ValidationError):
        LookupArgs(intent="other")


def test_lookup_rejects_extra_key():
    with pytest.raises(ValidationError):
        LookupArgs(intent="access", hack=True)


def test_answer_happy_path_parses_and_strips():
    args = AnswerArgs(question=" hi ", confidence="0.9", citations=["kb-1"])

    assert args.question == "hi"
    assert args.confidence == 0.9
    assert isinstance(args.confidence, float)
    assert args.citations == ["kb-1"]


def test_answer_rejects_blank_question():
    with pytest.raises(ValidationError):
        AnswerArgs(question="   ", confidence=0.1)


@pytest.mark.parametrize("confidence", [1.5, -0.1])
def test_answer_rejects_confidence_out_of_range(confidence):
    with pytest.raises(ValidationError):
        AnswerArgs(question="hi", confidence=confidence)


def test_answer_rejects_non_numeric_confidence():
    with pytest.raises(ValidationError):
        AnswerArgs(question="hi", confidence="nope")


@pytest.mark.parametrize("confidence", [0.9, 0.8])
def test_answer_high_confidence_requires_citation(confidence):
    # 0.8 is included: the bar is >= 0.8.
    with pytest.raises(ValidationError):
        AnswerArgs(question="hi", confidence=confidence, citations=[])


def test_answer_low_confidence_allows_no_citations():
    args = AnswerArgs(question="hi", confidence=0.79, citations=[])

    assert args.citations == []


def test_answer_rejects_extra_key():
    with pytest.raises(ValidationError):
        AnswerArgs(question="hi", confidence=0.1, extra=1)


def test_answer_default_citations_not_shared():
    first = AnswerArgs(question="q", confidence=0.1)
    second = AnswerArgs(question="q", confidence=0.1)

    assert first.citations is not second.citations
