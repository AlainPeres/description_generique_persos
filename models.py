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
- Only what cannot be computed from other values is stored (no derived
  values such as modifiers, bonuses or maximums computed from a formula)

Only the schema lives here. Per-system character data lives in systems/.
"""

from enum import Enum
from pydantic import Field, model_validator
from typing import Any, Self

from strict_model import StrictModel

# Union of every system-specific block, defined in systems/specific_values.py
# so that adding a new system never requires touching this file.
from systems.specific_values import SpecificValues, SpecificValuesDnD


# ---------------------------------------------------------------------------
# Utility classes: common to a large number of systems
# ---------------------------------------------------------------------------

# Enums inherit from str so that their values are written as plain strings
# in the JSON ("weapon", "Base"...) and read back from them.
class ItemCategory(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ITEM = "item"
    CONSUMABLE = "consumable"     # ammunition, potions, rations...
    MONEY = "money"               # coins, banknotes; the amount is the quantity


class EquipmentItem(StrictModel):
    name: str
    category: ItemCategory
    quantity: int = Field(default=1, ge=1)
    weight: float | None = None   # in kg; None = not tracked
    equipped: bool = False        # worn or in hand, as opposed to carried
    description: str = ""
    # Free-form game data (damage, range, charges...), keyed by name
    properties: dict[str, Any] = Field(default_factory=dict)


# Provenance of a skill or ability, not its type
class SkillCategory(str, Enum):
    BASE = "Base"                     # part of the system's official list
    NEW = "New"                       # added by the player (e.g. Cthulhu melee weapons)
    GENERIC = "Generic"               # open-ended skill, e.g. "Art (...)", "Pilot (...)"
    SPECIALIZATION = "Specialization" # a specialization of a generic skill


# Type of an ability, independent of its provenance (Ability.origin)
class AbilityCategory(str, Enum):
    FEAT = "Feat"                     # also Fate stunts
    ORIGIN_ABILITY = "Origin Ability" # granted by race, species, ancestry
    CLASS_ABILITY = "Class Ability"   # granted by a class or profession
    POWER = "Power"
    ADVANTAGE = "Advantage"           # also PF1 traits
    DISADVANTAGE = "Disadvantage"     # also PF1 drawbacks
    SPELL = "Spell"                   # spells are abilities, not a separate model


class Ability(StrictModel):
    name: str
    category: AbilityCategory
    value: int | None = None          # only for abilities that have a rating
    description: str = ""             # effect, conditions of use
    origin: SkillCategory = SkillCategory.BASE


class Skill(StrictModel):
    name: str
    category: SkillCategory
    # Its meaning is fixed per system, see specific_values.skill_value_meaning
    # (proficiency level, ranks, percentage...)
    value: int
    # None = the system has no skill checks; False/True = unchecked/checked.
    # Left out of the JSON when None.
    checked: bool | None = Field(default=None, exclude_if=lambda v: v is None)


# Any numeric stat: characteristics, current values (HP, Sanity...), AC...
class Attribute(StrictModel):
    name: str
    value: int


# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(StrictModel):
    # System-specific block; Pydantic picks its class from its `system` field
    specific_values: SpecificValues | None = None

    # Narrative fields, free text
    name: str = ""
    description: str = ""
    age: str = ""                     # free text: "34", "about forty", "ageless"
    occupation: str = ""
    background: str = ""
    additional_information: str = ""

    # Generic layer: name + value lists
    attributes: list[Attribute] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    abilities: list[Ability] = Field(default_factory=list)
    equipment: list[EquipmentItem] = Field(default_factory=list)
    # Possessions not described as equipment (house, land, shares...), free text
    possessions: list[str] = Field(default_factory=list)
    # Lasting effects (curse, disease, long-duration spell...), free text
    conditions: list[str] = Field(default_factory=list)

    # Cross-layer check: in D&D, prepared_spells (specific layer) names Spell
    # abilities (generic layer), so a typo would point to no spell. Names are
    # compared without case or surrounding spaces, as for classes.
    @model_validator(mode="after")
    def prepared_spells_are_known(self) -> Self:
        if isinstance(self.specific_values, SpecificValuesDnD):
            known = {a.name.strip().casefold() for a in self.abilities
                     if a.category == AbilityCategory.SPELL}
            unknown = [s for s in self.specific_values.prepared_spells
                       if s.strip().casefold() not in known]
            if unknown:
                raise ValueError(f"prepared spells without a matching Spell ability: {unknown}")
        return self
