"""
Pieces shared by the system modules: derived values, the fixed(...)
validator, character classes, the d20 abilities.

Each systems/<game>.py module holds everything specific to its rules (its
SpecificValuesXxx block, its derived values, its XxxCharacter class) and its
generic character template.
"""

from pydantic import AfterValidator, Field
from typing import Annotated, Literal

from models import AttributeCategory
from strict_model import StrictModel

# Conventions shared by every block:
# - every block whose system has skills declares `skill_value_meaning`: the
#   meaning of Skill.value is a fixed convention per system, written in each
#   JSON so the file explains itself; any other value is rejected;
# - only what remains is stored: maximums (slots per level, uses per day)
#   are derived. These two aliases only name the meaning of the numbers;
# - the model checks the structure only (types, enums, required and unknown
#   fields), never the rules of the game: a GM may allow anything, and rule
#   checks belong to the external calculator.
SpellLevel = int
Remaining = int


# ---------------------------------------------------------------------------
# Derived values: not stored, computed outside the model. Each system lists
# them in a fixed `derived_values` field, so that a reader of the JSON knows
# what exists and the external calculator knows what to produce.
# ---------------------------------------------------------------------------
class DerivedValue(StrictModel):
    name: str                 # e.g. "Armor Class"
    # One value for the character, or one per skill, or one per attribute of
    # the given category (the formula then reads the skill or attribute it
    # applies to)
    applies_to: Literal["character", "skill"] | AttributeCategory = "character"
    computed_from: str        # sources or formula, for the reader and the calculator


# Same behavior as a single-value Literal, for values Literal cannot hold
# (lists, models): the field has a default and any other value is rejected
def fixed[T](expected: T) -> AfterValidator:
    def check(value: T) -> T:
        if value != expected:
            raise ValueError("fixed by the system; do not edit")
        return value
    return AfterValidator(check)


# ---------------------------------------------------------------------------
# Character classes: common base of the class-based systems (D&D, PF1), each
# system adding its own fields
# ---------------------------------------------------------------------------
class CharacterClass(StrictModel):
    name: str                 # e.g. "Fighter"
    level: int                # a class taken again is a higher level, not a new entry

# The six abilities of the d20 systems, shared by D&D 5e and PF1
DnDAbility = Literal["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
