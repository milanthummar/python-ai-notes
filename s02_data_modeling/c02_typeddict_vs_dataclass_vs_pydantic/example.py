"""TypedDict vs dataclass vs Pydantic: same shape, three different runtimes.

Run directly:   python -m s02_data_modeling.c02_typeddict_vs_dataclass_vs_pydantic
Import + test:  from s02_data_modeling.c02_typeddict_vs_dataclass_vs_pydantic import from_dict_model

Pick by where the data came from: trusted internal state can stay a TypedDict
or dataclass; untrusted input at the edge goes through Pydantic.
"""
from dataclasses import dataclass
from typing import TypedDict, cast

from pydantic import BaseModel, ConfigDict, ValidationError


class AgentStateTD(TypedDict):
    """Type hint for a plain dict. Nothing is checked at runtime."""

    question: str
    retries: int


@dataclass
class AgentStateDC:
    """A real instance with fields, but no type validation."""

    question: str
    retries: int = 0


class AgentStateModel(BaseModel):
    """Validated model: rejects extra keys and wrong types (no coercion)."""

    model_config = ConfigDict(extra="forbid", strict=True)

    question: str
    retries: int = 0


def from_dict_typed(data: dict) -> AgentStateTD:
    """Return `data` unchanged. `cast` only informs the type checker.

    Extra keys stay, missing keys are not filled in, wrong types are kept.
    """
    return cast(AgentStateTD, data)


def from_dict_dataclass(data: dict) -> AgentStateDC:
    """Build an AgentStateDC from the two known keys.

    Missing `question` raises KeyError. Missing `retries` defaults to 0.
    Extra keys are ignored. Types are not checked.
    """
    return AgentStateDC(question=data["question"], retries=data.get("retries", 0))


def from_dict_model(data: dict) -> AgentStateModel:
    """Validate `data` strictly. Any problem raises ValidationError."""
    return AgentStateModel.model_validate(data)


def main() -> None:
    bad = {"question": "q", "retries": "3", "hack": True}

    print("typed:     ", from_dict_typed(bad))
    print("dataclass: ", from_dict_dataclass(bad))
    try:
        from_dict_model(bad)
    except ValidationError as exc:
        print("pydantic:  ", len(exc.errors()), "errors")


if __name__ == "__main__":
    main()
