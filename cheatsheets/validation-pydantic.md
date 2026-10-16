# Validation with Pydantic v2

_Grounded in JasonLo's repos as of 2026-06-06. Current practice is from the Pydantic v2.12 release notes and official docs._

## Reference snippet

```python
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Put a reusable constraint in the TYPE, not in a method of each model.
Confidence = Annotated[int, Field(ge=0, le=10)]


class Strict(BaseModel):
    # Declare the boundary policy one time. All subclasses inherit it.
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Decision(Strict):
    action: Literal["accept", "skip", "merge"]
    pick: str | None = None
    tags: list[str] = Field(default_factory=list)
    score: Confidence

    @model_validator(mode="after")
    def _check_pick(self) -> Decision:  # invariant across fields: use model_validator
        if self.action == "accept" and not self.pick:
            raise ValueError("action='accept' requires pick")
        return self


# At the boundary: parse the data. Do not construct the model and hope that it is valid.
d = Decision.model_validate({"action": "accept", "pick": "x", "score": 7})
payload = d.model_dump(mode="json")  # not .dict() or .json()
```

## Typical usage patterns

- **Strict base model at the boundary.** A shared parent sets `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Each model for I/O that inherits it rejects unknown keys and validates again on each change. (seen in `JasonLo/best-in-slot:bis/models.py`, the `_Strict` base)
- **Field constraints, not hand-written checks.** `Field(min_length=1)`, `Field(ge=0, le=10)`, `Field(pattern=...)`, and `Field(default=3, ge=1, le=10)` put the rule on the field. Then the rule is part of the schema. (seen in `JasonLo/best-in-slot:bis/models.py` and `bis/config.py`)
- **`model_validator(mode="after")` for rules across fields.** Use it when a rule applies to many fields, for example "action X requires field Y". The validator runs on the complete instance and returns `self`. (seen in `JasonLo/best-in-slot:bis/models.py`, the `_check_pick` validators)

## Learnings

- **A generated default is a step after construction** → **A generated default belongs to the field**. The call `Field(default_factory=lambda: uuid4().hex[:8])` declares a default `id` on the field. Use `model_post_init` only for calculated state across many fields. (seen in a private time-tracking model)
- **You build the object and then trust it** → **The model is a parse boundary**. Untrusted input enters through `Model.model_validate(data)` and leaves through `model_dump(mode="json")`, not `parse_obj`/`.dict()`/`.json()`. The model converts unknown data into a trusted instance.
- **`from __future__ import annotations` helps Pydantic resolve types** → **Python 3.14 evaluates annotations only when code uses them, and the import now causes errors**. With Pydantic v2.12 on Python 3.14, the import causes `ClassVar` NameErrors and `TypedDict`/`Required` failures. Remove it. (seen in `JasonLo/best-in-slot:bis/models.py` and `bis/config.py`)

## Agent rules

- ALWAYS write simple value bounds as `Field(ge=, le=, min_length=, pattern=)` or an `Annotated[...]` alias.
- NEVER write a custom validator that only checks a range again.
- ALWAYS limit `@field_validator` and `@model_validator(mode="after")` to logic across fields or other custom logic.
- ALWAYS return `self` from after-validators.
- ALWAYS declare the boundary policy one time in a shared base with `model_config = ConfigDict(extra="forbid", validate_assignment=True)`.
- ALWAYS use `ConfigDict(alias_generator=..., populate_by_name=True)` for a uniform camelCase boundary.
- ALWAYS limit an `alias=` on a single field to irregular single names.
- ALWAYS use `Field(default_factory=...)` for mutable or generated defaults.
- NEVER use `model_post_init` to set the default of a single field.
- ALWAYS write PEP 604 and PEP 585 annotations, for example `X | None` and `list[X]`, not `Optional[X]` and `List[X]`.
- ALWAYS use `model_validate`, `model_dump`, and `model_dump_json` at the boundary.
- NEVER use the v1 `parse_obj`, `.dict()`, or `.json()` methods.
- NEVER use `class Config:` in v2.
- NEVER add `from __future__ import annotations` to Pydantic code on Python 3.14 or later.
