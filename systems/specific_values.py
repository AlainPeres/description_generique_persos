"""
System-specific value blocks, one per RPG system.

Kept separate from models.py so that models.py can build the
specific_values Union from ALL_SPECIFIC_VALUES without each system
module having to import Character (which would create a circular
import, since systems/<game>.py modules import Character to build
their generic character templates).

To add a new system: define its SpecificValuesXxx(BaseModel) class
here (with a `system: Literal[...]` discriminator field) and append
it to ALL_SPECIFIC_VALUES.
"""

from pydantic import BaseModel, Field
from typing import Literal


# ---------------------------------------------------------------------------
# System-specific block: Dungeons & Dragons 5e
# ---------------------------------------------------------------------------
class SpecificValuesDnD(BaseModel):
    system: Literal["dnd5e"]
    character_class: str
    race: str
    level: int
    alignment: str
    size: str | None = None
    speed: dict[str, int] = Field(default_factory=dict)
    languages: list[str] = Field(default_factory=list)
    reflex_save: int
    fortitude_save: int
    will_save: int


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
class SpecificValuesCthulhu(BaseModel):
    system: Literal["cthulhu6"]


# ---------------------------------------------------------------------------
# System-specific block: Fate
# ---------------------------------------------------------------------------
class SpecificValuesFate(BaseModel):
    system: Literal["fate"]
    Concept: str
    Aspects: list[str] = Field(default_factory=list)
    Stunts: list[str] = Field(default_factory=list)
    Extras: list[str] = Field(default_factory=list)
    FatePoints: int


# ---------------------------------------------------------------------------
# System-specific block: SagaS
# ---------------------------------------------------------------------------
class SpecificValuesSagas(BaseModel):
    system: Literal["SagaS"]


# ---------------------------------------------------------------------------
# Registry: every system-specific class must be listed here to be usable
# as Character.specific_values
# ---------------------------------------------------------------------------
ALL_SPECIFIC_VALUES: list[type[BaseModel]] = [
    SpecificValuesDnD,
    SpecificValuesCthulhu,
    SpecificValuesFate,
    SpecificValuesSagas,
]
