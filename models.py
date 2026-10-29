"""
RPG character schema (multi-system) with Pydantic.

Architecture:
- A common base (Character) with two complementary layers:
  1. Generic layer: attributes, skills, abilities, equipment
     (system-agnostic, usable across all RPGs; spells are an Ability with
     category=SPELL)
  2. Optional system-specific block (specific_values: SpecificValuesDnD | SpecificValuesCthulhu | ...)
     for systems whose structure cannot be expressed as name+value pairs
     (e.g. FATE Aspects, Stunts, Extras)
- All Character fields are optional (default to empty / None)

Only the schema lives here. Per-system character data lives in systems/.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Annotated, Union

from systems.specific_values import ALL_SPECIFIC_VALUES

# Union of every registered system-specific block, built from the list in
# systems/specific_values.py instead of enumerated here, so that adding a
# new system never requires touching this file. `discriminator="system"`
# lets Pydantic pick the right subtype directly from the `system` field
# instead of trying each member in turn.
SpecificValues = Annotated[
    Union[tuple(ALL_SPECIFIC_VALUES)], Field(discriminator="system")
]


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

class SkillCategory(str, Enum):
    BASE = "Base"
    NEW = "New"
    GENERIC = "Generic"
    SPECIALIZATION = "Specialization"

class AbilityCategory(str, Enum):
    FEAT = "Feat"
    ORIGIN_ABILITY = "Origin Ability"
    CLASS_ABILITY = "Class Ability"
    POWER = "Power"
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"
    SPELL = "Spell"

class Ability(BaseModel):
    name: str
    category: AbilityCategory
    value: int
    description: str = ""
    origin: SkillCategory = SkillCategory.BASE

class Skill(BaseModel):
    name: str
    category: SkillCategory
    value: int

class Attribute(BaseModel):
    name: str
    value: int


# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(BaseModel):
    specific_values: SpecificValues | None = None
    name: str = ""
    description: str = ""
    occupation: str = ""
    background: str = ""
    additional_information: str=""
    attributes: list[Attribute] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    abilities: list[Ability] = Field(default_factory=list)
    equipment: list[EquipmentItem] = Field(default_factory=list)
