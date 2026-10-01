"""Pydantic at the edges: validate untrusted input once, at the boundary.

Run directly:   python -m s02_data_modeling.c01_pydantic_at_the_edges
Import + test:  from s02_data_modeling.c01_pydantic_at_the_edges import LookupArgs, AnswerArgs

Tool arguments emitted by an LLM are untrusted, same as user input. Parsing
them into a model fails fast with `ValidationError` before any work runs.
"""
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


class DefaultModel(BaseModel):
    """Shared config: reject unknown keys and strip whitespace from strings."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LookupArgs(DefaultModel):
    """Arguments for a lookup tool. `intent` must be "access" or "billing"."""

    intent: str = Field(min_length=1)

    @field_validator("intent", mode="after")
    @classmethod
    def lookup_intent(cls, value: str) -> str:
        """Allow only known intents. Runs after stripping, so " access " passes."""
        if value not in {"access", "billing"}:
            raise ValueError("intent should be 'access' or 'billing'")
        return value


class AnswerArgs(DefaultModel):
    """Arguments for an answer tool.

    `confidence` is a float in [0, 1]. At 0.8 or above, at least one citation
    is required.
    """

    question: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    citations: list[str] = Field(default_factory=list)

    @field_validator("confidence", mode="before")
    @classmethod
    def convert_value(cls, value: object) -> object:
        """Turn a numeric string like "0.9" into a float before type checking.

        A non-numeric string raises ValueError, which Pydantic reports as
        ValidationError. Other values pass through to the normal checks.
        """
        if isinstance(value, str):
            return float(value)
        return value

    @model_validator(mode="after")
    def lookup_answer(self) -> "AnswerArgs":
        """Cross-field rule: high confidence needs at least one citation."""
        if self.confidence >= 0.8 and not self.citations:
            raise ValueError("citations should be provided if confidence is high")
        return self


def main() -> None:
    print("valid:  ", AnswerArgs(question=" hi ", confidence="0.9", citations=["kb-1"]))

    try:
        AnswerArgs(question="hi", confidence=0.9)
    except ValidationError as exc:
        print("invalid:", exc.errors()[0]["msg"])


if __name__ == "__main__":
    main()
