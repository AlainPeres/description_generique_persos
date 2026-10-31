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

# Only what remains is stored: maximums (slots per level, uses per day) are derived
SpellLevel = Annotated[int, Field(ge=1, le=9)]
Remaining = Annotated[int, Field(ge=0)]

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
    saving_throw_proficiencies: list[str] = Field(default_factory=list)  # e.g. ["Strength", "Constitution"]
    # State between two rests
    exhaustion: int = Field(default=0, ge=0, le=6)
    inspiration: bool = False
    hit_dice_remaining: int | None = Field(default=None, ge=0)     # None = all available
    # Slots are shared by all classes; pact magic (warlock) is separate
    spell_slots_remaining: dict[SpellLevel, Remaining] = Field(default_factory=dict)
    pact_slots_remaining: int | None = Field(default=None, ge=0)   # None = no warlock levels
    prepared_spells: list[str] = Field(default_factory=list)       # names of Spell abilities
    resources_remaining: dict[str, Remaining] = Field(default_factory=dict)  # e.g. {"Ki": 3}

    @field_validator("classes")
    @classmethod
    def no_duplicate_class(cls, classes: list[DnDClass]) -> list[DnDClass]:
        return check_unique_class_names(classes)


def check_unique_class_names[C: DnDClass | PF1Class](classes: list[C]) -> list[C]:
    names = [c.name.strip().casefold() for c in classes]
    if len(names) != len(set(names)):
        raise ValueError("each class must appear only once; raise its level instead")
    return classes


# ---------------------------------------------------------------------------
# System-specific block: Pathfinder 1st edition
# ---------------------------------------------------------------------------
class PreparedSpell(StrictModel):
    name: str
    level: int = Field(ge=0, le=9)
    cast: bool = False        # already used since it was prepared

class PF1Class(StrictModel):
    name: str                                            # e.g. "Fighter"
    archetypes: list[str] = Field(default_factory=list)  # PF1 allows several per class
    level: int = Field(ge=1, le=20)
    # Each class has its own spells per day
    spells_remaining: dict[SpellLevel, Remaining] = Field(default_factory=dict)  # spontaneous casters
    prepared_spells: list[PreparedSpell] = Field(default_factory=list)          # prepared casters

class SpecificValuesPF1(StrictModel):
    system: Literal["pf1"]
    # One entry per class; the total level is their sum, so it is not stored
    classes: list[PF1Class] = Field(min_length=1)
    favored_class: str = ""
    race: str
    experience_points: int = Field(default=0, ge=0)
    alignment: str
    deity: str = ""
    size: str | None = None
    speed: dict[str, int] = Field(default_factory=dict)
    languages: list[str] = Field(default_factory=list)
    # Class skills granted by traits; those from the class lists are derived
    additional_class_skills: list[str] = Field(default_factory=list)
    # Lasting states, e.g. {"Strength": 2}
    ability_damage: dict[str, int] = Field(default_factory=dict)
    ability_drain: dict[str, int] = Field(default_factory=dict)
    negative_levels: int = Field(default=0, ge=0)
    hero_points: int | None = Field(default=None, ge=0)   # None = optional rule not used
    resources_remaining: dict[str, Remaining] = Field(default_factory=dict)  # e.g. {"Rage rounds": 5}

    @field_validator("classes")
    @classmethod
    def no_duplicate_class(cls, classes: list[PF1Class]) -> list[PF1Class]:
        return check_unique_class_names(classes)


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
    | SpecificValuesPF1
    | SpecificValuesCthulhu
    | SpecificValuesFate
    | SpecificValuesSagas
    | SpecificValuesNoRules,
    Field(discriminator="system"),
]
