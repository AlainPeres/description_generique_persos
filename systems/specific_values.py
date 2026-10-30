"""
System-specific value blocks, one per RPG system.

Kept separate from models.py so that models.py can import the
SpecificValues union without each system module having to import
Character (which would create a circular import, since
systems/<game>.py modules import Character to build their generic
character templates).

To add a new system: define its SpecificValuesXxx(StrictModel) class
here (with a `system: Literal[...]` discriminator field) and add it
to the SpecificValues union at the bottom of this file.
"""

from pydantic import Field, field_validator
from typing import Annotated, Literal

from strict_model import StrictModel

# ---------------------------------------------------------------------------
# System-specific block: No Rules
# ---------------------------------------------------------------------------
class SpecificValuesNoRules(StrictModel):
    system: Literal["norules"]   
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# System-specific block: Dungeons & Dragons 5e
# ---------------------------------------------------------------------------
class DnDClass(StrictModel):
    name: str                 # e.g. "Fighter"
    subclass: str = ""        # e.g. "Battle Master"; empty before it is chosen
    level: int = Field(ge=1, le=20)

class SpecificValuesDnD(StrictModel):
    system: Literal["dnd5e"]
    # One entry per class (several when multiclassing); the total level is
    # the sum of the class levels, so it is not stored
    classes: list[DnDClass] = Field(min_length=1)
    race: str
    experience_points: int = Field(default=0, ge=0)
    alignment: str
    size: str | None = None
    speed: dict[str, int] = Field(default_factory=dict)
    languages: list[str] = Field(default_factory=list)

    @field_validator("classes")
    @classmethod
    def no_duplicate_class(cls, classes: list[DnDClass]) -> list[DnDClass]:
        names = [c.name.strip().casefold() for c in classes]
        if len(names) != len(set(names)):
            raise ValueError("each class must appear only once; raise its level instead")
        return classes


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
class MentalDisorder(StrictModel):
    name: str                 # e.g. "Claustrophobia"
    duration: Literal["temporary", "indefinite", "permanent"]
    description: str = ""     # circumstances, effects
    cured: bool = False

class SpecificValuesCthulhu(StrictModel):
    system: Literal["cthulhu6"]
    mental_disorders: list[MentalDisorder] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# System-specific block: Fate
# ---------------------------------------------------------------------------
class StressBox(StrictModel):
    available: bool = True    # the box exists for this character
    checked: bool = False     # the box is ticked

class Consequence(StrictModel):
    available: bool = True    # the slot exists for this character
    value: int                # stress absorbed: 2, 4 or 6 depending on severity
    text: str = ""            # the consequence suffered, e.g. "Broken arm"

class SpecificValuesFate(StrictModel):
    system: Literal["fate"]
    HighConcept: str
    Trouble: str
    Aspects: list[str] = Field(default_factory=list,max_length=3)
    Extras: list[str] = Field(default_factory=list)
    FatePoints: int
    Refresh: int
    PhysicalStress: dict[str, StressBox] = Field(default_factory=dict, max_length=4)
    MentalStress: dict[str, StressBox] = Field(default_factory=dict, max_length=4)
    Consequences: dict[str, Consequence] = Field(default_factory=dict, max_length=5)

# ---------------------------------------------------------------------------
# System-specific block: SagaS
# ---------------------------------------------------------------------------
class SpecificValuesSagas(StrictModel):
    system: Literal["sagas"]
    unspent_creation_points: int = Field(default=0, ge=0)  # set aside for later
    serious_physical_injuries: list[str] = Field(default_factory=list)
    serious_psychical_injuries: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Registry: every system-specific class must be listed here to be usable
# as Character.specific_values. Written out explicitly so that type checkers
# (Pylance, mypy) know each member. `discriminator="system"` lets Pydantic
# pick the right subtype directly from the `system` field instead of trying
# each member in turn.
# ---------------------------------------------------------------------------
SpecificValues = Annotated[
    SpecificValuesDnD
    | SpecificValuesCthulhu
    | SpecificValuesFate
    | SpecificValuesSagas
    | SpecificValuesNoRules,
    Field(discriminator="system"),
]
