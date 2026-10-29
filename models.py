"""
RPG character schema (multi-system) with Pydantic.

Architecture:
- A common base (Character) with two complementary layers:
  1. Generic layer: attributes, skills, abilities, equipment
     (system-agnostic, usable across all RPGs; spells are an Ability with
     category=SPELL)
  2. Optional system-specific block (specific_values: SpecificValuesDnD | SpecificValuesCthulhu | ...)
     for systems whose structure cannot be expressed as name+value pairs
     (e.g. FATE Aspects, Stress, Extras)
- All Character fields are optional (default to empty / None)

Only the schema lives here. Per-system character data lives in systems/.
"""

from enum import Enum
from pydantic import Field
from typing import Any

from strict_model import StrictModel

# Union of every system-specific block, defined in systems/specific_values.py
# so that adding a new system never requires touching this file.
from systems.specific_values import SpecificValues


# ---------------------------------------------------------------------------
#Utility Classes: common to large number of systems
# ---------------------------------------------------------------------------

class ItemCategory(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ITEM = "item"
    CONSUMABLE = "consumable"


class EquipmentItem(StrictModel):
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

class Ability(StrictModel):
    name: str
    category: AbilityCategory
    value: int | None = None
    description: str = ""
    origin: SkillCategory = SkillCategory.BASE

class Skill(StrictModel):
    name: str
    category: SkillCategory
    value: int
    # None = the system has no skill checks; False/True = unchecked/checked
    checked: bool | None = Field(default=None, exclude_if=lambda v: v is None)

class Attribute(StrictModel):
    name: str
    value: int


# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(StrictModel):
    specific_values: SpecificValues | None = None
    name: str = ""
    description: str = ""
    age: str = ""
    occupation: str = ""
    background: str = ""
    additional_information: str=""
    attributes: list[Attribute] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    abilities: list[Ability] = Field(default_factory=list)
    equipment: list[EquipmentItem] = Field(default_factory=list)
