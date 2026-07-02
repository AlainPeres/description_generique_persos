"""
RPG character schema (multi-system) with Pydantic.

Architecture:
- A common base (Character) with two complementary layers:
  1. Generic layer: attributes, skills, abilities, spells, equipment
     (system-agnostic, usable across all RPGs)
  2. Optional system-specific block (specific_values: SpecificValuesDnD | SpecificValuesCthulhu | ...)
     for systems whose structure cannot be expressed as name+value pairs
     (e.g. FATE Aspects, Stunts, Extras)
- All Character fields are optional (default to empty / None)

Only the schema lives here. Per-system character data lives in systems/.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Any


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
    Concept:str
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
#Utility Classes: common to large number of systems
# ---------------------------------------------------------------------------

class ItemCategory(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ITEM = "item"
    CONSUMABLE = "consumable"


class EquipmentItem(BaseModel):
    name: str
    category: ItemCategory
    quantity: int = Field(default=1, ge=1)
    weight: float | None = None  # in kg
    equipped: bool = False
    description: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)

class AbilityCategory(str, Enum):
    FEAT = "Feat"
    ORIGIN_ABILITY = "Origin Ability"
    CLASS_ABILITY = "Class Ability"
    POWER = "Power"
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"

class Ability(BaseModel):
    name: str
    category: AbilityCategory
    value: int

class SkillCategory(str, Enum):
    BASE = "Base"
    NEW = "New"
    GENERIC = "Generic"
    SPECIALIZATION = "Specialization"

class Skill(BaseModel):
    name: str
    category: SkillCategory
    value: int

class Attribute(BaseModel):
    name: str
    value: int

class SpellCategory(str, Enum):
    BASE = "Base"
    NEW = "New"

class Spell(BaseModel):
    name: str
    category: SpellCategory
    description: str = ""


# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(BaseModel):
    specific_values: SpecificValuesDnD | SpecificValuesCthulhu | SpecificValuesFate | SpecificValuesSagas | None = None
    name: str = ""
    description: str = ""
    occupation: str = ""
    background: str = ""
    attributes: list[Attribute] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    abilities: list[Ability] = Field(default_factory=list)
    spells: list[Spell] = Field(default_factory=list)
    equipment: list[EquipmentItem] = Field(default_factory=list)
