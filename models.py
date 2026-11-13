"""
RPG character schema (multi-system) with Pydantic.

Architecture:
- A common base (Character) with two complementary layers:
  1. Generic layer: attributes, skills, abilities, equipment, conditions
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

import re
from enum import Enum
from pydantic import Field, model_validator
from typing import Any, Literal, Self

from strict_model import StrictModel
# Shared with systems/specific_values.py (DerivedValue.applies_to)
from attribute_category import AttributeCategory

# Union of every system-specific block, defined in systems/specific_values.py
# so that adding a new system never requires touching this file.
from systems.specific_values import (
    DAREDEVILS_ATTRIBUTES, DAREDEVILS_TALENTS, OPENQUEST_CHARACTERISTICS, SAGAS_SKILL_ATTRIBUTES,
    SpecificValues, SpecificValuesDaredevils, SpecificValuesDnD, SpecificValuesOpenQuest,
    SpecificValuesSagas,
)


# Names used in a skill base formula ("Deftness + Wit + Natural",
# "Dexterity + 10", "Power * 3"): the operands that are not numbers, in order
def base_names(base: str) -> list[str]:
    operands = (t.strip() for t in re.split(r"[-+*/()]", base))
    return [t for t in operands if t and not t.isdigit()]


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
    # Provenance, independent of category: Base = from the official rules,
    # New = added by the player or the GM (house spell, custom stunt, super
    # power outside the base rules...). Generic and Specialization make no
    # sense here. Descriptive only: no validator reads it.
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
    # How the skill is computed from the attributes, as a readable formula:
    # "Agility" (SagaS), "Deftness + Wit + Natural" (Daredevils initial score;
    # the first attribute and the first talent govern), "Dexterity + 10"
    # (OpenQuest base). Filled in the templates for listed skills; required
    # for NEW skills in SagaS and Daredevils. Left out of the JSON when None.
    base: str | None = Field(default=None, exclude_if=lambda v: v is None)


# Any numeric stat: characteristics, current values (HP, Sanity...)...
class Attribute(StrictModel):
    name: str
    category: AttributeCategory
    value: int


# What a lasting condition affects
class ConditionKind(str, Enum):
    PHYSICAL = "Physical"             # injury, disease, poison...
    MENTAL = "Mental"                 # Cthulhu mental disorder; also covers what
                                      # SagaS calls "Psychical" (psychical injury)
    OTHER = "Other"                   # curse, long-duration spell, magical effect...


# A lasting state described in text. Numeric states used by the rules
# (D&D exhaustion, PF1 ability damage, Fate consequences...) stay in
# specific_values.
class Condition(StrictModel):
    name: str                         # e.g. "Claustrophobia", "Broken leg"
    kind: ConditionKind
    # None = not specified by the system
    duration: Literal["temporary", "indefinite", "permanent"] | None = None
    description: str = ""             # circumstances, effects
    cured: bool = False               # kept for the character's history


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
    # Lasting effects: curse, disease, Cthulhu mental disorder, SagaS serious
    # physical or psychical injury...
    conditions: list[Condition] = Field(default_factory=list)

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

    # Cross-layer check: in SagaS, a skill is based on one attribute, among
    # the main and secondary ones; a NEW skill must declare it (the template
    # gives it for listed skills).
    @model_validator(mode="after")
    def sagas_skill_bases(self) -> Self:
        if isinstance(self.specific_values, SpecificValuesSagas):
            for skill in self.skills:
                if skill.base is None:
                    if skill.category == SkillCategory.NEW:
                        raise ValueError(f"new skill {skill.name!r} needs a base attribute")
                    continue
                names = base_names(skill.base)
                if len(names) != 1 or names[0] not in SAGAS_SKILL_ATTRIBUTES:
                    raise ValueError(
                        f"skill {skill.name!r}: base must be one attribute among "
                        f"{list(SAGAS_SKILL_ATTRIBUTES)}, got {skill.base!r}")
        return self

    # Cross-layer checks for Daredevils: skill scores are not negative; a
    # base names attributes and talents, starting with the governing attribute
    # and holding the governing talent; a NEW skill must declare one; freely
    # improvable skills name skills of the character.
    @model_validator(mode="after")
    def daredevils_skills(self) -> Self:
        sv = self.specific_values
        if not isinstance(sv, SpecificValuesDaredevils):
            return self
        for skill in self.skills:
            if skill.value < 0:
                raise ValueError(f"skill {skill.name!r}: score must not be negative")
            if skill.base is None:
                if skill.category == SkillCategory.NEW:
                    raise ValueError(f"new skill {skill.name!r} needs a base formula")
                continue
            names = base_names(skill.base)
            unknown = [n for n in names if n not in DAREDEVILS_ATTRIBUTES + DAREDEVILS_TALENTS]
            if (unknown or not names or names[0] not in DAREDEVILS_ATTRIBUTES
                    or not any(n in DAREDEVILS_TALENTS for n in names)):
                raise ValueError(
                    f"skill {skill.name!r}: base must start with a governing attribute "
                    f"and hold a talent, got {skill.base!r}")
        known = {s.name.strip().casefold() for s in self.skills}
        unknown = [s for s in sv.freely_improvable_skills if s.strip().casefold() not in known]
        if unknown:
            raise ValueError(f"freely improvable skills without a matching skill: {unknown}")
        return self

    # Cross-layer checks for OpenQuest: 100% is the upper limit for skills; a
    # base names characteristics; divine_spells_cast names Spell abilities,
    # compared as prepared_spells.
    @model_validator(mode="after")
    def openquest_checks(self) -> Self:
        sv = self.specific_values
        if isinstance(sv, SpecificValuesOpenQuest):
            for skill in self.skills:
                if not 0 <= skill.value <= 100:
                    raise ValueError(f"skill {skill.name!r}: percentage must be between 0 and 100")
                if skill.base is not None:
                    unknown = [n for n in base_names(skill.base) if n not in OPENQUEST_CHARACTERISTICS]
                    if unknown:
                        raise ValueError(
                            f"skill {skill.name!r}: base names unknown characteristics {unknown}")
            known = {a.name.strip().casefold() for a in self.abilities
                     if a.category == AbilityCategory.SPELL}
            unknown = [s for s in sv.divine_spells_cast if s.strip().casefold() not in known]
            if unknown:
                raise ValueError(f"cast divine spells without a matching Spell ability: {unknown}")
        return self
