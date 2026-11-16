"""
SagaS: system-specific block and derived values, the SagasCharacter
class, and the generic character template.

Default values ("to be specified", characteristics of 5, skill levels for the
initial learning levels) are meant to be replaced when describing an actual character. "Psychical"
is the system's own term and is kept as is.
"""

from typing import Annotated, Literal

from models import CharacterBase, Attribute, AttributeCategory, Skill, SkillCategory
from strict_model import StrictModel
from systems.common import DerivedValue, fixed


# ---------------------------------------------------------------------------
# System-specific block: SagaS
# ---------------------------------------------------------------------------
SAGAS_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Learning Levels", applies_to="skill", computed_from="skill level - associated attribute"),
    DerivedValue(name="Protection",
                 computed_from="Armor + Abilities (super powers, outside the base rules); 0 by default"),
    DerivedValue(name="MaxImpactBonus", computed_from="2*Protection + Physical Shock Threshold"),
    DerivedValue(name="Physical Hit Points", computed_from="2*(Strength + Will + Endurance)"),
    DerivedValue(name="Psychical Hit Points", computed_from="2*(Presence + Will + Instinct)"),
    DerivedValue(name="Physical Shock Threshold", computed_from="10 + UT Strength bonus"),
    DerivedValue(name="Psychical Shock Threshold", computed_from="10 + UT Presence bonus"),
    DerivedValue(name="Reflex Defense", computed_from="2 + Dodge skill level / 2, rounded down"),
    # The secondary characteristics are stored as final values; the creation
    # points bought for each are deduced from them
    DerivedValue(name="Initiative Creation Bonus",
                 computed_from="Initiative - (Agility + Wit) / 2, rounded down"),
    DerivedValue(name="Close Combat Creation Bonus",
                 computed_from="Close Combat - (Strength + 2*Agility + Instinct + Will) / 5, rounded down"),
    DerivedValue(name="Ranged Combat Creation Bonus",
                 computed_from="Ranged Combat - (3*Dexterity + 2*Instinct) / 5, rounded down"),
    DerivedValue(name="Speed Creation Bonus",
                 computed_from="Speed - species base (6 for humans) - (Endurance + Agility) / 4, rounded down"),
)

class SpecificValuesSagas(StrictModel):
    # The final skill level is stored, so the sheet reads as played; the
    # learning level (bought with points) is derived. The attribute associated
    # with each skill is fixed by the rules
    skill_value_meaning: Literal["skill level (associated attribute + learning level)"] = (
        "skill level (associated attribute + learning level)"
    )
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(SAGAS_DERIVED)] = SAGAS_DERIVED
    unspent_creation_points: int = 0  # set aside for later
    # Current wounds and stun are attributes; serious injuries are
    # CharacterBase.conditions, kind Physical, or kind Mental for psychical ones


class SagasCharacter(CharacterBase):
    system: Literal["sagas"]
    specific_values: SpecificValuesSagas


# ---------------------------------------------------------------------------
# Generic template
# ---------------------------------------------------------------------------
generic_sagas = SagasCharacter(
    system="sagas",
    name="Generic SagaS Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    occupation="to be specified",
    additional_information="to be specified",   
    specific_values=SpecificValuesSagas(),
    attributes=[
        # Characteristics
        Attribute(name="Strength", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Agility", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Endurance", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Dexterity", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Wit", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Will", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Presence", category=AttributeCategory.MAIN, value=5),
        Attribute(name="Instinct", category=AttributeCategory.MAIN, value=5),

        # Secondary characteristics: computed from the main ones plus the
        # creation points bought for them. The final values are stored, so the
        # sheet reads as played; the creation bonuses are derived from them.
        # Recompute a total when a main characteristic changes (here, bonus 0)
        Attribute(name="Initiative", category=AttributeCategory.SECONDARY, value=5),
        Attribute(name="Close Combat", category=AttributeCategory.SECONDARY, value=5),
        Attribute(name="Ranged Combat", category=AttributeCategory.SECONDARY, value=5),
        Attribute(name="Speed", category=AttributeCategory.SECONDARY, value=8),

        # Current wounds and stun; lasting serious injuries are kept apart,
        # as text, in specific_values
        Attribute(name="Physical Wounds", category=AttributeCategory.STATE, value=0),
        Attribute(name="Psychical Wounds", category=AttributeCategory.STATE, value=0),
        Attribute(name="Physical Stun", category=AttributeCategory.STATE, value=0),
        Attribute(name="Psychical Stun", category=AttributeCategory.STATE, value=0),
        # Protection and MaxImpactBonus are derived from other values, so
        # they are not stored
    ],
    # Value = skill level (associated attribute + learning level), the value
    # played; the learning level is derived. Here, with every main and
    # secondary characteristic at 5, except Speed (8) for the Speed-based
    # skills from Run on, the level is the attribute + the initial learning
    # level. GENERIC skills are open-ended ("Other Arts (...)")
    skills=[
        Skill(name="Arm Wrestling", category=SkillCategory.BASE, value=5, base="Strength"),
        Skill(name="Weight Lifting", category=SkillCategory.BASE, value=5, base="Strength"),
        Skill(name="Weight Throwing", category=SkillCategory.BASE, value=5, base="Strength"),

        Skill(name="Climb", category=SkillCategory.BASE, value=5, base="Agility"),
        Skill(name="Acrobatics", category=SkillCategory.BASE, value=-10, base="Agility"),
        Skill(name="Stealth", category=SkillCategory.BASE, value=5, base="Agility"),
        Skill(name="Dodge", category=SkillCategory.BASE, value=5, base="Agility"),
        Skill(name="Dance", category=SkillCategory.BASE, value=5, base="Agility"),

        Skill(name="Lockpicking", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Sleight of Hand", category=SkillCategory.BASE, value=-10, base="Dexterity"),
        Skill(name="Driving Car", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Motorcycle Driving", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Airplane Piloting", category=SkillCategory.BASE, value=-5, base="Dexterity"),
        Skill(name="Helicopter Piloting", category=SkillCategory.BASE, value=-5, base="Dexterity"),
        Skill(name="Driving Aquatic Machine", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Driving Heavy Vehicle", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Pilot Spacecraft", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Other Driving", category=SkillCategory.GENERIC, value=0, base="Dexterity"),
        Skill(name="Other Piloting", category=SkillCategory.GENERIC, value=-5, base="Dexterity"),
        Skill(name="Battle Armor", category=SkillCategory.BASE, value=0, base="Dexterity"),
        Skill(name="Games of Accuracy", category=SkillCategory.GENERIC, value=0, base="Dexterity"),

        Skill(name="Physical Resistance", category=SkillCategory.BASE, value=5, base="Endurance"),

        Skill(name="General Culture", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Native Language", category=SkillCategory.BASE, value=5, base="Wit"),
        Skill(name="Investigation", category=SkillCategory.BASE, value=5, base="Wit"),
        Skill(name="Computer Science", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Security Systems", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Explosives", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Electricity", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Electronics", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Mechanical", category=SkillCategory.BASE, value=-5, base="Wit"),
        Skill(name="Physics", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Chemistry", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Astronomy", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Zoology", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Botanical", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Biology", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Geology", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Archaeology", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="History", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Paleontology", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Law", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Medicine", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Psychiatry", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Occultism", category=SkillCategory.BASE, value=-10, base="Wit"),
        Skill(name="Handcrafts", category=SkillCategory.GENERIC, value=-5, base="Wit"),
        Skill(name="Other Knowledges", category=SkillCategory.GENERIC, value=-10, base="Wit"),
        Skill(name="Foreign Languages", category=SkillCategory.GENERIC, value=-10, base="Wit"),
        Skill(name="Other Sciences", category=SkillCategory.GENERIC, value=-10, base="Wit"),
        Skill(name="Other Techniques", category=SkillCategory.GENERIC, value=-5, base="Wit"),
        Skill(name="Mind Games", category=SkillCategory.GENERIC, value=0, base="Wit"),

        Skill(name="Mental Resistance", category=SkillCategory.BASE, value=5, base="Will"),

        Skill(name="Persuasion", category=SkillCategory.BASE, value=5, base="Presence"),
        Skill(name="Intimidation", category=SkillCategory.BASE, value=5, base="Presence"),
        Skill(name="Interrogation", category=SkillCategory.BASE, value=5, base="Presence"),
        Skill(name="Command", category=SkillCategory.BASE, value=5, base="Presence"),
        Skill(name="Disguise", category=SkillCategory.BASE, value=-5, base="Presence"),
        Skill(name="Bluff", category=SkillCategory.BASE, value=5, base="Presence"),
        Skill(name="Charm", category=SkillCategory.BASE, value=5, base="Presence"),
        Skill(name="Eloquence", category=SkillCategory.BASE, value=5, base="Presence"),

        Skill(name="Perception", category=SkillCategory.BASE, value=5, base="Instinct"),
        Skill(name="Psychology", category=SkillCategory.BASE, value=0, base="Instinct"),
        Skill(name="Pedagogy", category=SkillCategory.BASE, value=5, base="Instinct"),
        Skill(name="First Aid", category=SkillCategory.BASE, value=-5, base="Instinct"),
        Skill(name="Animal Handling", category=SkillCategory.BASE, value=0, base="Instinct"),
        Skill(name="Tracking", category=SkillCategory.BASE, value=-5, base="Instinct"),
        Skill(name="Survival", category=SkillCategory.BASE, value=0, base="Instinct"),
        Skill(name="Horse Riding", category=SkillCategory.BASE, value=-5, base="Instinct"),
        Skill(name="Painting", category=SkillCategory.BASE, value=-10, base="Instinct"),
        Skill(name="Music", category=SkillCategory.BASE, value=-10, base="Instinct"),
        Skill(name="Singing", category=SkillCategory.BASE, value=-10, base="Instinct"),
        Skill(name="Writing", category=SkillCategory.BASE, value=-10, base="Instinct"),
        Skill(name="Sculpture", category=SkillCategory.BASE, value=-10, base="Instinct"),
        Skill(name="Dramatic Art", category=SkillCategory.BASE, value=-10, base="Instinct"),
        Skill(name="Other Arts", category=SkillCategory.GENERIC, value=-10, base="Instinct"),

        Skill(name="Brawling", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Axe/Mace", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Dagger", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Sword", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="2-Handed Sword", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Axe/Mace with 2 hands", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Flail", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Spear", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Polearm", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Shield", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Lance", category=SkillCategory.BASE, value=5, base="Close Combat"),
        Skill(name="Close Combat with 2 weapons", category=SkillCategory.BASE, value=-5, base="Close Combat"),
        Skill(name="Draw Weapon on Contact", category=SkillCategory.BASE, value=-5, base="Close Combat"),
        Skill(name="Martial Arts", category=SkillCategory.GENERIC, value=-10, base="Close Combat"),

        Skill(name="Bow", category=SkillCategory.BASE, value=0, base="Ranged Combat"),
        Skill(name="Crossbow", category=SkillCategory.BASE, value=5, base="Ranged Combat"),
        Skill(name="Throwing Dagger", category=SkillCategory.BASE, value=0, base="Ranged Combat"),
        Skill(name="Throwing Axe", category=SkillCategory.BASE, value=0, base="Ranged Combat"),
        Skill(name="Sling", category=SkillCategory.BASE, value=0, base="Ranged Combat"),
        Skill(name="Throw", category=SkillCategory.BASE, value=5, base="Ranged Combat"),
        Skill(name="Javelin", category=SkillCategory.BASE, value=5, base="Ranged Combat"),
        Skill(name="Gun", category=SkillCategory.BASE, value=5, base="Ranged Combat"),
        Skill(name="Rifle", category=SkillCategory.BASE, value=5, base="Ranged Combat"),
        Skill(name="Automatic Weapon", category=SkillCategory.BASE, value=5, base="Ranged Combat"),
        Skill(name="Draw Weapon", category=SkillCategory.BASE, value=-5, base="Ranged Combat"),
        Skill(name="Combat with 2 ranged Weapons", category=SkillCategory.BASE, value=-5, base="Ranged Combat"),
        Skill(name="Heavy Weapons", category=SkillCategory.GENERIC, value=-5, base="Ranged Combat"),

        Skill(name="Run", category=SkillCategory.BASE, value=8, base="Speed"),
        Skill(name="Jump", category=SkillCategory.BASE, value=8, base="Speed"),
        Skill(name="Swimming", category=SkillCategory.BASE, value=3, base="Speed"),
        Skill(name="Cycling", category=SkillCategory.BASE, value=8, base="Speed"),
        Skill(name="Skiing", category=SkillCategory.BASE, value=-7, base="Speed"),
        Skill(name="Tennis", category=SkillCategory.BASE, value=-7, base="Speed"),
        Skill(name="Hang-Glider", category=SkillCategory.BASE, value=-2, base="Speed"),
        Skill(name="Sail", category=SkillCategory.BASE, value=-2, base="Speed"),
        Skill(name="Skydiving", category=SkillCategory.BASE, value=3, base="Speed"),
        Skill(name="Diving", category=SkillCategory.BASE, value=3, base="Speed"),
        Skill(name="Other Sports", category=SkillCategory.GENERIC, value=8, base="Speed"),
    ],
)
