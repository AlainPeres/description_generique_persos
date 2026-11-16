"""
Call of Cthulhu 6th edition: system-specific block and derived values, the CthulhuCharacter
class, and the generic character template.

Default values ("to be specified", base skill percentages) are meant to be
replaced when describing an actual investigator.
"""

from typing import Annotated, Literal

from models import CharacterBase, Attribute, AttributeCategory, Skill, SkillCategory
from strict_model import StrictModel
from systems.common import DerivedValue, fixed


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
CTHULHU_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Idea", computed_from="Intelligence x 5"),
    DerivedValue(name="Luck", computed_from="Power x 5"),
    DerivedValue(name="Know", computed_from="Education x 5"),
    DerivedValue(name="Damage Bonus", computed_from="Strength + Size, damage bonus table"),
    DerivedValue(name="Maximum Sanity", computed_from="99 - Cthulhu Mythos"),
    DerivedValue(name="Maximum Hit Points", computed_from="(Constitution + Size) / 2, rounded up"),
    DerivedValue(name="Maximum Magic Points", computed_from="Power"),
)

class SpecificValuesCthulhu(StrictModel):
    skill_value_meaning: Literal["percentage"] = "percentage"
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(CTHULHU_DERIVED)] = CTHULHU_DERIVED
    # Everything else lives in the generic layer: characteristics, current
    # Sanity, skills and their improvement checks, and mental disorders
    # (CharacterBase.conditions, kind Mental, duration temporary / indefinite /
    # permanent)


class CthulhuCharacter(CharacterBase):
    system: Literal["cthulhu6"]
    specific_values: SpecificValuesCthulhu


# ---------------------------------------------------------------------------
# Generic template
# ---------------------------------------------------------------------------
generic_cthulhu6 = CthulhuCharacter(
    system="cthulhu6",
    name="Generic Cthulhu 6 Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    occupation="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesCthulhu(),
    attributes=[
        Attribute(name="Strength", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Constitution", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Size", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Dexterity", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Appearance", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Intelligence", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Power", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Education", category=AttributeCategory.MAIN, value=10),
        # Only current values: the maximums are derived (Sanity 99 - Cthulhu
        # Mythos, Hit Points (CON+SIZ)/2, Magic Points POW), as are Idea,
        # Luck, Know (INT, POW, EDU x5) and the damage bonus
        Attribute(name="Current Sanity", category=AttributeCategory.STATE, value=10),
        Attribute(name="Current Hit Points", category=AttributeCategory.STATE, value=10),
        Attribute(name="Current Magic Points", category=AttributeCategory.STATE, value=10),
        Attribute(name="Move", category=AttributeCategory.SECONDARY, value=8),
    ],
    # Value = percentage. checked=False: improvement check not ticked yet.
    # Melee weapon skills are deliberately left out: players add the ones
    # they use as SkillCategory.NEW.
    skills=[
        Skill(name="Accounting", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Anthropology", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Archaeology", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Art", category=SkillCategory.GENERIC, value=5, checked=False),
        Skill(name="Astronomy", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Bargain", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="Biology", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Chemistry", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Climb", category=SkillCategory.BASE, value=40, checked=False),
        Skill(name="Computer Use", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Conceal", category=SkillCategory.BASE, value=15, checked=False),
        Skill(name="Craft", category=SkillCategory.GENERIC, value=5, checked=False),
        Skill(name="Credit Rating", category=SkillCategory.BASE, value=15, checked=False),
        # No check: Cthulhu Mythos never improves through experience
        Skill(name="Cthulhu Mythos", category=SkillCategory.BASE, value=0),
        Skill(name="Disguise", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Dodge", category=SkillCategory.BASE, value=20, checked=False),
        Skill(name="Drive Auto", category=SkillCategory.BASE, value=20, checked=False),
        Skill(name="Electr. Repair", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Electronics", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Fast Talk", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="First Aid", category=SkillCategory.BASE, value=30, checked=False),
        Skill(name="Geology", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Hide", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="History", category=SkillCategory.BASE, value=20, checked=False),
        Skill(name="Jump", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Law", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="Library Use", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Listen", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Locksmith", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Martial Arts", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Mech. Repair", category=SkillCategory.BASE, value=20, checked=False),
        Skill(name="Medicine", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="Natural History", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Navigate", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Occult", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="Opr. Hvy. Mch.", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Other Languages", category=SkillCategory.GENERIC, value=1, checked=False),
        Skill(name="Own Language", category=SkillCategory.BASE, value=50, checked=False),
        Skill(name="Persuade", category=SkillCategory.BASE, value=15, checked=False),
        Skill(name="Pharmacy", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Photography", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Physics", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Pilot", category=SkillCategory.GENERIC, value=1, checked=False),
        Skill(name="Psychoanalysis", category=SkillCategory.BASE, value=1, checked=False),
        Skill(name="Psychology", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="Ride", category=SkillCategory.BASE, value=5, checked=False),
        Skill(name="Sneak", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Spot Hidden", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Swim", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Throw", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Track", category=SkillCategory.BASE, value=10, checked=False),
        # Firearms
        Skill(name="Handgun", category=SkillCategory.BASE, value=20, checked=False),
        Skill(name="Machine Gun", category=SkillCategory.BASE, value=15, checked=False),
        Skill(name="Rifle", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Shotgun", category=SkillCategory.BASE, value=30, checked=False),
        Skill(name="SMG", category=SkillCategory.BASE, value=15, checked=False),
        # Unarmed attacks
        Skill(name="Fist", category=SkillCategory.BASE, value=50, checked=False),
        Skill(name="Grapple", category=SkillCategory.BASE, value=25, checked=False),
        Skill(name="Head", category=SkillCategory.BASE, value=10, checked=False),
        Skill(name="Kick", category=SkillCategory.BASE, value=25, checked=False),
    ],
)
