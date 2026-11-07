"""
Generic OpenQuest 3 character template.

Default values ("to be specified", the 30 creation points spread evenly over
the characteristics, skills at their base) are meant to be replaced when
describing an actual character. A non-human's species goes in `description`,
its traits and natural weapons in `abilities`.
"""

from models import Character, Attribute, Skill, SkillCategory
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
        Attribute(name="Strength", value=12),
        Attribute(name="Constitution", value=12),
        Attribute(name="Dexterity", value=12),
        Attribute(name="Size", value=13),
        Attribute(name="Intelligence", value=13),
        Attribute(name="Power", value=12),
        Attribute(name="Charisma", value=12),
        # Only current values: the maximums are derived (Hit Points
        # (SIZ+CON)/2 rounded up, Magic Points POW), as are the damage
        # modifier and the movement rate
        Attribute(name="Current Hit Points", value=13),
        Attribute(name="Current Magic Points", value=12),
    ],
    # Value = percentage (0 to 100), here the base computed from the
    # characteristics above. GENERIC skills must be specified:
    # "Lore (Heraldry)", "Language (Goblinoid)"...
    skills=[
        # Resistances
        Skill(name="Dodge", category=SkillCategory.BASE, value=22),             # DEX+10
        Skill(name="Persistence", category=SkillCategory.BASE, value=22),       # POW+10
        Skill(name="Resilience", category=SkillCategory.BASE, value=24),        # CON+POW

        # Combat skills
        Skill(name="Close Combat", category=SkillCategory.BASE, value=24),      # DEX+STR
        Skill(name="Ranged Combat", category=SkillCategory.BASE, value=25),     # DEX+INT
        Skill(name="Unarmed Combat", category=SkillCategory.BASE, value=24),    # DEX+STR

        # Knowledge skills
        Skill(name="Culture (Own)", category=SkillCategory.BASE, value=23),     # INT+10
        Skill(name="Language (Own)", category=SkillCategory.BASE, value=63),    # INT+50
        Skill(name="Natural Lore", category=SkillCategory.BASE, value=23),      # INT+10
        Skill(name="Culture (Other)", category=SkillCategory.GENERIC, value=13),   # INT
        Skill(name="Language (Other)", category=SkillCategory.GENERIC, value=13),  # INT
        Skill(name="Lore", category=SkillCategory.GENERIC, value=13),             # INT

        # Practical skills
        Skill(name="Athletics", category=SkillCategory.BASE, value=24),         # DEX+STR
        Skill(name="Craft", category=SkillCategory.BASE, value=23),             # INT+10
        Skill(name="Deception", category=SkillCategory.BASE, value=25),         # DEX+INT
        Skill(name="Driving", category=SkillCategory.BASE, value=25),           # DEX+INT
        Skill(name="Engineering", category=SkillCategory.BASE, value=23),       # INT+10
        Skill(name="Healing", category=SkillCategory.BASE, value=23),           # INT+10
        Skill(name="Influence", category=SkillCategory.BASE, value=22),         # CHA+10
        Skill(name="Mechanisms", category=SkillCategory.BASE, value=25),        # DEX+INT
        Skill(name="Perception", category=SkillCategory.BASE, value=25),        # INT+POW
        Skill(name="Performance", category=SkillCategory.BASE, value=22),       # CHA+10
        Skill(name="Riding", category=SkillCategory.BASE, value=24),            # DEX+POW
        Skill(name="Sailing", category=SkillCategory.BASE, value=25),           # DEX+INT
        Skill(name="Streetwise", category=SkillCategory.BASE, value=24),        # CHA+POW
        Skill(name="Trade", category=SkillCategory.BASE, value=23),             # INT+10
        Skill(name="Wealth", category=SkillCategory.BASE, value=25),            # INT+CHA, optional rule

        # Magic skills
        Skill(name="Personal Magic Casting", category=SkillCategory.BASE, value=36),  # POW x 3
        Skill(name="Sorcery Casting", category=SkillCategory.BASE, value=13),         # INT
        Skill(name="Religion (Own)", category=SkillCategory.BASE, value=23),          # INT+10
        Skill(name="Religion (Other)", category=SkillCategory.GENERIC, value=13),     # INT
    ],
)
