# Validation with Pydantic v2

_Grounded in JasonLo's repos as of 2026-06-06; current practice per Pydantic v2.12 release notes and official docs._

## Reference snippet

```python
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Reusable constraint lives in the TYPE, not a per-model method.
Confidence = Annotated[int, Field(ge=0, le=10)]


class Strict(BaseModel):
    # Boundary policy declared once, inherited everywhere.
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Decision(Strict):
    action: Literal["accept", "skip", "merge"]
    pick: str | None = None
    tags: list[str] = Field(default_factory=list)
    score: Confidence

    @model_validator(mode="after")
    def _check_pick(self) -> Decision:  # cross-field invariant → model_validator
        if self.action == "accept" and not self.pick:
            raise ValueError("action='accept' requires pick")
        return self


# At the boundary: parse, don't construct-and-hope.
d = Decision.model_validate({"action": "accept", "pick": "x", "score": 7})
payload = d.model_dump(mode="json")  # not .dict()/.json()
```

## Typical usage patterns

- **Strict boundary base model** — a shared parent carrying `model_config = ConfigDict(extra="forbid", validate_assignment=True)` so every I/O-crossing model rejects unknown keys and re-validates on mutation. You reach for this whenever data comes from YAML/JSON/subprocess/LLM and you want unexpected fields to fail loudly rather than silently drop. (seen in `JasonLo/best-in-slot:bis/models.py`, the `_Strict` base)
- **Declarative field constraints over hand-written checks** — `Field(min_length=1)`, `Field(ge=0, le=10)`, `Field(pattern=...)`, `Field(default=3, ge=1, le=10)` carry the rule on the field itself. The intent ("this is a non-empty string / a bounded int") is part of the schema, not buried in a method. (seen in `JasonLo/best-in-slot:bis/models.py` and `bis/config.py`)
- **`model_validator(mode="after")` for cross-field invariants** — when a rule spans multiple fields (e.g. "action X requires field Y"), an after-validator runs on the fully-built instance and returns `self`. This is the home for conditional-requirement logic that no single `Field` can express. (seen in `JasonLo/best-in-slot:bis/models.py`, the per-action `_check_pick` validators)

## Learnings

- **"Every rule is a `@validator` method"** → **"The constraint belongs to the type."** A 0–10 bound written as a custom validator function reimplements what `Field(ge=0, le=10)` (or an `Annotated[int, Field(ge=0, le=10)]` alias) states declaratively. v2's mental model: simple value bounds are *schema*, not procedure — reserve validators for logic the type system genuinely can't express (cross-field, side-effecting, parse-then-coerce). (seen in a private LLM-screening model, where a `validate_confidence` function duplicates a plain range bound)
- **"Generate derived defaults in `model_post_init`"** → **"A self-generating default belongs to the field."** Filling a blank `id` after construction reconstructs imperatively what `Field(default_factory=lambda: uuid4().hex[:8])` declares at the field. `model_post_init` is for cross-field derived state; a single field's default-on-absence is a property of that field. (seen in a private time-tracking model)
- **"Build the object, then trust it"** → **"Parse at the boundary with `model_validate`."** Untrusted input (dict from YAML/JSON/an LLM) should enter through `Model.model_validate(data)` and leave through `model_dump(mode="json")` — not the v1 `parse_obj`/`.dict()`/`.json()` trio. The shift is treating the model as a *parse boundary* that converts unknown data into a trusted instance, not just a container you populate.
- **"`from __future__ import annotations` helps Pydantic resolve types"** → **"Python 3.14 natively defers annotations; the import now conflicts."** PEP 563 (the `__future__` import) stringifies all annotations, clashing with Pydantic v2.12's type-resolution on Python 3.14 — causing `ClassVar` NameErrors and `TypedDict`/`Required` failures (pydantic/pydantic#12393, #12421). Python 3.14 adopted PEP 649, making lazy annotation evaluation the default; the import is unnecessary and harmful on 3.14+. Drop it; Pydantic v2.12 handles deferred annotations correctly without it. (seen in `JasonLo/best-in-slot:bis/models.py` and `bis/config.py`)

## Agent rules

- ALWAYS express simple value bounds as `Field(ge=, le=, min_length=, pattern=)` or an `Annotated[...]` alias — never a custom validator that only re-checks a range.
- ALWAYS reserve `@field_validator` / `@model_validator(mode="after")` for cross-field or genuinely custom logic; return `self` from after-validators.
- ALWAYS declare boundary policy once via a shared base with `model_config = ConfigDict(extra="forbid", validate_assignment=True)` for I/O-crossing models.
- ALWAYS use `ConfigDict(alias_generator=..., populate_by_name=True)` for a uniform camelCase boundary instead of per-field `alias=`; reserve per-field `alias=` for irregular one-off names.
- ALWAYS use `Field(default_factory=...)` for mutable or self-generating defaults — never `model_post_init` for a single field's default-on-absence, never a bare `= []` when a factory reads more clearly.
- ALWAYS write annotations as `X | None` / `list[X]` (PEP 604/585), not `Optional[X]` / `List[X]`.
- ALWAYS cross the boundary with `model_validate` / `model_dump` / `model_dump_json` — NEVER the v1 `parse_obj` / `.dict()` / `.json()`.
- NEVER use `class Config:` — it's `model_config = ConfigDict(...)` in v2.
- NEVER add `from __future__ import annotations` to Python 3.14+ Pydantic code — Python 3.14 evaluates annotations lazily by default (PEP 649); mixing it with Pydantic v2.12's type resolution causes `ClassVar` and `TypedDict`/`Required` failures.
