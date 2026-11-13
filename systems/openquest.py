"""
Generic OpenQuest 3 character template.

Default values ("to be specified", the 30 creation points spread evenly over
the characteristics, skills at their base) are meant to be replaced when
describing an actual character. A non-human's species goes in `description`,
its traits and natural weapons in `abilities`.
"""

from models import Character, Attribute, AttributeCategory, Skill, SkillCategory
from systems.specific_values import SpecificValuesOpenQuest

generic_openquest3 = Character(
    name="Generic OpenQuest 3 Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    occupation="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesOpenQuest(system="openquest3"),
    attributes=[
        # 8 each + 30 points (3 to 18 at creation, 21 at most for a human;
        # INT and SIZ never below 8, SIZ never grows)
        Attribute(name="Strength", category=AttributeCategory.MAIN, value=12),
        Attribute(name="Constitution", category=AttributeCategory.MAIN, value=12),
        Attribute(name="Dexterity", category=AttributeCategory.MAIN, value=12),
        Attribute(name="Size", category=AttributeCategory.MAIN, value=13),
        Attribute(name="Intelligence", category=AttributeCategory.MAIN, value=13),
        Attribute(name="Power", category=AttributeCategory.MAIN, value=12),
        Attribute(name="Charisma", category=AttributeCategory.MAIN, value=12),
        # Only current values: the maximums are derived (Hit Points
        # (SIZ+CON)/2 rounded up, Magic Points POW), as are the damage
        # modifier and the movement rate
        Attribute(name="Current Hit Points", category=AttributeCategory.STATE, value=13),
        Attribute(name="Current Magic Points", category=AttributeCategory.STATE, value=12),
    ],
    # Value = percentage (0 to 100), here the base computed from the
    # characteristics above. GENERIC skills must be specified:
    # "Lore (Heraldry)", "Language (Goblinoid)"...
    skills=[
        # Resistances
        Skill(name="Dodge", category=SkillCategory.BASE, value=22, base="Dexterity + 10"),
        Skill(name="Persistence", category=SkillCategory.BASE, value=22, base="Power + 10"),
        Skill(name="Resilience", category=SkillCategory.BASE, value=24, base="Constitution + Power"),

        # Combat skills
        Skill(name="Close Combat", category=SkillCategory.BASE, value=24, base="Dexterity + Strength"),
        Skill(name="Ranged Combat", category=SkillCategory.BASE, value=25, base="Dexterity + Intelligence"),
        Skill(name="Unarmed Combat", category=SkillCategory.BASE, value=24, base="Dexterity + Strength"),

        # Knowledge skills
        Skill(name="Culture (Own)", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Language (Own)", category=SkillCategory.BASE, value=63, base="Intelligence + 50"),
        Skill(name="Natural Lore", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Culture (Other)", category=SkillCategory.GENERIC, value=13, base="Intelligence"),
        Skill(name="Language (Other)", category=SkillCategory.GENERIC, value=13, base="Intelligence"),
        Skill(name="Lore", category=SkillCategory.GENERIC, value=13, base="Intelligence"),

        # Practical skills
        Skill(name="Athletics", category=SkillCategory.BASE, value=24, base="Dexterity + Strength"),
        Skill(name="Craft", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Deception", category=SkillCategory.BASE, value=25, base="Dexterity + Intelligence"),
        Skill(name="Driving", category=SkillCategory.BASE, value=25, base="Dexterity + Intelligence"),
        Skill(name="Engineering", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Healing", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Influence", category=SkillCategory.BASE, value=22, base="Charisma + 10"),
        Skill(name="Mechanisms", category=SkillCategory.BASE, value=25, base="Dexterity + Intelligence"),
        Skill(name="Perception", category=SkillCategory.BASE, value=25, base="Intelligence + Power"),
        Skill(name="Performance", category=SkillCategory.BASE, value=22, base="Charisma + 10"),
        Skill(name="Riding", category=SkillCategory.BASE, value=24, base="Dexterity + Power"),
        Skill(name="Sailing", category=SkillCategory.BASE, value=25, base="Dexterity + Intelligence"),
        Skill(name="Streetwise", category=SkillCategory.BASE, value=24, base="Charisma + Power"),
        Skill(name="Trade", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Wealth", category=SkillCategory.BASE, value=25, base="Intelligence + Charisma"),  # optional rule

        # Magic skills
        Skill(name="Personal Magic Casting", category=SkillCategory.BASE, value=36, base="Power * 3"),
        Skill(name="Sorcery Casting", category=SkillCategory.BASE, value=13, base="Intelligence"),
        Skill(name="Religion (Own)", category=SkillCategory.BASE, value=23, base="Intelligence + 10"),
        Skill(name="Religion (Other)", category=SkillCategory.GENERIC, value=13, base="Intelligence"),
    ],
)
