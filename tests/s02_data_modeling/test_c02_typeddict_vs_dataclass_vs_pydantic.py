import pytest
from pydantic import ValidationError

from s02_data_modeling.c02_typeddict_vs_dataclass_vs_pydantic import (
    AgentStateDC,
    AgentStateModel,
    from_dict_dataclass,
    from_dict_model,
    from_dict_typed,
)


def test_typed_returns_same_dict():
    data = {"question": "q", "retries": 1}

    assert from_dict_typed(data) is data


def test_typed_keeps_extras_and_wrong_types():
    data = {"question": "q", "retries": "nope", "hack": True}

    result = from_dict_typed(data)

    assert result["hack"] is True
    assert result["retries"] == "nope"


def test_dataclass_defaults_retries():
    result = from_dict_dataclass({"question": "q"})

    assert isinstance(result, AgentStateDC)
    assert result.retries == 0


def test_dataclass_ignores_extra_key():
    result = from_dict_dataclass({"question": "q", "retries": 2, "hack": True})

    assert result == AgentStateDC(question="q", retries=2)


def test_dataclass_does_not_validate_types():
    result = from_dict_dataclass({"question": "q", "retries": "nope"})

    assert result.retries == "nope"


def test_dataclass_missing_question_raises_key_error():
    with pytest.raises(KeyError):
        from_dict_dataclass({"retries": 1})


def test_model_defaults_retries():
    assert from_dict_model({"question": "q"}).retries == 0


def test_model_accepts_good_payload():
    result = from_dict_model({"question": "q", "retries": 2})

    assert isinstance(result, AgentStateModel)
    assert result.question == "q"
    assert result.retries == 2


@pytest.mark.parametrize(
    "data",
    [
        {"question": "q", "retries": 1, "hack": True},  # extra key
        {"question": "q", "retries": "3"},  # strict: no "3" -> 3
        {"question": 123},  # strict: no 123 -> "123"
        {"retries": 1},  # missing question
    ],
)
def test_model_rejects_bad_payload(data):
    with pytest.raises(ValidationError):
        from_dict_model(data)
