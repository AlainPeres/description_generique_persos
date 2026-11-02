"""
Generic SagaS character template.

Default values ("to be specified", characteristics of 5, base learning levels)
are meant to be replaced when describing an actual character. "Psychical"
is the system's own term and is kept as is.
"""

from models import Character, Attribute, Skill, SkillCategory
from systems.specific_values import SpecificValuesSagas

generic_sagas = Character(
    name="Generic SagaS Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    occupation="to be specified",
    additional_information="to be specified",   
    specific_values=SpecificValuesSagas(system="sagas"),
    attributes=[
        # Characteristics
        Attribute(name="Strength", value=5),
        Attribute(name="Agility", value=5),
        Attribute(name="Endurance", value=5),
        Attribute(name="Dexterity", value=5),
        Attribute(name="Wit", value=5),
        Attribute(name="Will", value=5),
        Attribute(name="Presence", value=5),
        Attribute(name="Instinct", value=5),

        # Combat values
        Attribute(name="Initiative", value=5),
        Attribute(name="Close Combat", value=5),
        Attribute(name="Ranged Combat", value=5),
        Attribute(name="Speed", value=8),

        # Current wounds and stun; lasting serious injuries are kept apart,
        # as text, in specific_values
        Attribute(name="Physical Wounds", value=0),
        Attribute(name="Psychical Wounds", value=0),
        Attribute(name="Physical Stun", value=0),
        Attribute(name="Psychical Stun", value=0),
        # Protection and MaxImpactBonus are derived from other values, so
        # they are not stored
    ],
    # Value = learning level; the skill level (associated attribute +
    # learning level) is derived. GENERIC skills are open-ended ("Climb (...)")
    skills=[
        Skill(name="Arm Wrestling", category=SkillCategory.BASE, value=0),
        Skill(name="Weight Lifting", category=SkillCategory.BASE, value=0),
        Skill(name="Weight Throwing", category=SkillCategory.BASE, value=0),

        Skill(name="Climb", category=SkillCategory.GENERIC, value=10),
        Skill(name="Acrobatics", category=SkillCategory.BASE, value=-15),
        Skill(name="Stealth", category=SkillCategory.BASE, value=0),
        Skill(name="Dodge", category=SkillCategory.BASE, value=0),
        Skill(name="Dance", category=SkillCategory.BASE, value=0),

        Skill(name="Lockpicking", category=SkillCategory.BASE, value=-5),
        Skill(name="Sleight of Hand", category=SkillCategory.BASE, value=-15),
        Skill(name="Driving Car", category=SkillCategory.GENERIC, value=-5),
        Skill(name="Motorcycle Driving", category=SkillCategory.BASE, value=-5),
        Skill(name="Airplane Piloting", category=SkillCategory.BASE, value=-10),
        Skill(name="Helicopter Piloting", category=SkillCategory.BASE, value=-10),
        Skill(name="Driving Aquatic Machine", category=SkillCategory.BASE, value=-5),
        Skill(name="Driving Heavy Vehicle", category=SkillCategory.BASE, value=-5),
        Skill(name="Pilot Spacecraft", category=SkillCategory.BASE, value=-5),
        Skill(name="Battle Armor", category=SkillCategory.BASE, value=-5),
        Skill(name="Games of Accuracy", category=SkillCategory.GENERIC, value=0),

        Skill(name="Physical Resistance", category=SkillCategory.BASE, value=0),

        Skill(name="General Culture", category=SkillCategory.BASE, value=-10),
        Skill(name="Native Language", category=SkillCategory.BASE, value=0),
        Skill(name="Investigation", category=SkillCategory.BASE, value=0),
        Skill(name="Computer Science", category=SkillCategory.BASE, value=-10),
        Skill(name="Security Systems", category=SkillCategory.BASE, value=-10),
        Skill(name="Explosives", category=SkillCategory.BASE, value=-10),
        Skill(name="Electricity", category=SkillCategory.BASE, value=-10),
        Skill(name="Electronics", category=SkillCategory.BASE, value=-10),
        Skill(name="Mechanical", category=SkillCategory.BASE, value=-10),
        Skill(name="Physics", category=SkillCategory.BASE, value=-15),
        Skill(name="Chemistry", category=SkillCategory.BASE, value=-15),
        Skill(name="Astronomy", category=SkillCategory.BASE, value=-15),
        Skill(name="Zoology", category=SkillCategory.BASE, value=-15),
        Skill(name="Botanical", category=SkillCategory.BASE, value=-15),
        Skill(name="Biology", category=SkillCategory.BASE, value=-15),
        Skill(name="Geology", category=SkillCategory.GENERIC, value=-15),
        Skill(name="Archaeology", category=SkillCategory.BASE, value=-15),
        Skill(name="History", category=SkillCategory.BASE, value=-15),
        Skill(name="Paleontology", category=SkillCategory.BASE, value=-15),
        Skill(name="Law", category=SkillCategory.BASE, value=-15),
        Skill(name="Medicine", category=SkillCategory.BASE, value=-15),
        Skill(name="Psychiatry", category=SkillCategory.GENERIC, value=-15),
        Skill(name="Occultism", category=SkillCategory.BASE, value=-15),
        Skill(name="Handcrafts", category=SkillCategory.GENERIC, value=-10),
        Skill(name="Other Knowledges",category=SkillCategory.GENERIC, value=-15),
        Skill(name="Foreign Languages", category=SkillCategory.GENERIC, value=-15),
        Skill(name="Other Sciences", category=SkillCategory.GENERIC, value=-15),
        Skill(name="Other Techniques", category=SkillCategory.GENERIC, value=-10),
        Skill(name="Mind Games", category=SkillCategory.GENERIC, value=-5),

        Skill(name="Mental Resistance", category=SkillCategory.BASE, value=0),

        Skill(name="Persuasion", category=SkillCategory.BASE, value=0),
        Skill(name="Intimidation", category=SkillCategory.BASE, value=0),
        Skill(name="Interrogation", category=SkillCategory.BASE, value=0),
        Skill(name="Command", category=SkillCategory.BASE, value=0),
        Skill(name="Disguise", category=SkillCategory.BASE, value=-10),
        Skill(name="Bluff", category=SkillCategory.BASE, value=0),
        Skill(name="Charm", category=SkillCategory.BASE, value=0),
        Skill(name="Eloquence", category=SkillCategory.BASE, value=0),

        Skill(name="Perception", category=SkillCategory.BASE, value=0),
        Skill(name="Psychology", category=SkillCategory.BASE, value=-5),
        Skill(name="Pedagogy", category=SkillCategory.BASE, value=0),
        Skill(name="First Aid", category=SkillCategory.GENERIC, value=-10),
        Skill(name="Animal Handling", category=SkillCategory.BASE, value=0),
        Skill(name="Tracking", category=SkillCategory.BASE, value=-10),
        Skill(name="Survival", category=SkillCategory.BASE, value=-5),
        Skill(name="Horse Riding", category=SkillCategory.BASE, value=-10),
        Skill(name="Painting", category=SkillCategory.BASE, value=-15),
        Skill(name="Music", category=SkillCategory.BASE, value=-15),
        Skill(name="Writing", category=SkillCategory.BASE, value=-15),
        Skill(name="Sculpture", category=SkillCategory.BASE, value=-15),
        Skill(name="Dramatic Art", category=SkillCategory.BASE, value=-15),
        Skill(name="Other Arts", category=SkillCategory.GENERIC, value=-15),

        Skill(name="Brawling", category=SkillCategory.BASE, value=0),
        Skill(name="Axe/Mace", category=SkillCategory.BASE, value=0),
        Skill(name="Dagger", category=SkillCategory.BASE, value=0),
        Skill(name="Sword", category=SkillCategory.BASE, value=0),
        Skill(name="2-Handed Sword", category=SkillCategory.BASE, value=0),
        Skill(name="Axe/Mace with 2 hands", category=SkillCategory.BASE, value=0),
        Skill(name="Flail", category=SkillCategory.BASE, value=0),
        Skill(name="Spear", category=SkillCategory.BASE, value=0),
        Skill(name="Hast Weapon", category=SkillCategory.BASE, value=0),
        Skill(name="Shield", category=SkillCategory.BASE, value=0),
        Skill(name="Cavalry Spear", category=SkillCategory.BASE, value=0),
        Skill(name="Close Combat with 2 weapons", category=SkillCategory.BASE, value=-10),
        Skill(name="Draw Weapon on Contact", category=SkillCategory.BASE, value=-10),
        Skill(name="Martial Arts", category=SkillCategory.GENERIC, value=-15),

        Skill(name="Bow", category=SkillCategory.BASE, value=-5),
        Skill(name="Crossbow", category=SkillCategory.BASE, value=0),
        Skill(name="Throwing Dagger", category=SkillCategory.BASE, value=-5),
        Skill(name="Throwing Axe", category=SkillCategory.BASE, value=-5),
        Skill(name="Sling", category=SkillCategory.BASE, value=-5),
        Skill(name="Throw", category=SkillCategory.BASE, value=0),
        Skill(name="Javelin", category=SkillCategory.BASE, value=0),
        Skill(name="Gun", category=SkillCategory.BASE, value=0),
        Skill(name="Automatic Weapon", category=SkillCategory.BASE, value=0),
        Skill(name="Draw Weapon", category=SkillCategory.BASE, value=-10),
        Skill(name="Combat with 2 ranged Weapons", category=SkillCategory.BASE, value=-10),
        Skill(name="Heavy Weapons", category=SkillCategory.GENERIC, value=-10),

        Skill(name="Run", category=SkillCategory.BASE, value=0),
        Skill(name="Jump", category=SkillCategory.BASE, value=0),
        Skill(name="Swimming", category=SkillCategory.BASE, value=-5),
        Skill(name="Skiing", category=SkillCategory.BASE, value=-15),
        Skill(name="Tennis", category=SkillCategory.BASE, value=-15),
        Skill(name="Hang-Glider", category=SkillCategory.BASE, value=-10),
        Skill(name="Sail", category=SkillCategory.BASE, value=-10),
        Skill(name="Skydiving", category=SkillCategory.BASE, value=-5),
        Skill(name="Diving", category=SkillCategory.BASE, value=-5),
        Skill(name="Other Sports", category=SkillCategory.GENERIC, value=0),
    ],
)
