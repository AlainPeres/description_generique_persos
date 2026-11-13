"""
Generic D&D 5th edition character template.

Default values ("to be specified", ability scores of 10) are meant to be
replaced when describing an actual character.
"""

from models import Character, Attribute, AttributeCategory, Skill, SkillCategory, Ability, AbilityCategory
from systems.specific_values import SpecificValuesDnD, DnDClass

generic_dnd5e = Character(
    name="Generic D&D 5e Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesDnD(
        system="dnd5e",
        classes=[DnDClass(name="to be specified", level=1)],
        race="to be specified",
        alignment="to be specified",
        size="Medium",
        speed={"walk": 30},
        languages=["Common"],
    ),
    attributes=[
        Attribute(name="Strength", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Dexterity", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Constitution", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Intelligence", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Wisdom", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Charisma", category=AttributeCategory.MAIN, value=10),

        # Maximum HP is stored: it is rolled at each level. Armor Class,
        # modifiers, proficiency bonus, initiative and passive Perception are
        # derived (AC from class, race, armor, shield, items and active
        # spells), so they are not stored.
        Attribute(name="Maximum Hit Points", category=AttributeCategory.SECONDARY, value=10),
        Attribute(name="Current Hit Points", category=AttributeCategory.STATE, value=10),
    ],
    # Skill value = proficiency level: 0 none, 1 proficient, 2 expertise;
    # the total bonus is derived from it, the ability modifier and the level
    skills=[
        Skill(name="Acrobatics", category=SkillCategory.BASE, value=0),
        Skill(name="Animal Handling", category=SkillCategory.BASE, value=0),
        Skill(name="Arcana", category=SkillCategory.BASE, value=0),
        Skill(name="Athletics", category=SkillCategory.BASE, value=0),
        Skill(name="Deception", category=SkillCategory.BASE, value=0),
        Skill(name="History", category=SkillCategory.BASE, value=0),
        Skill(name="Insight", category=SkillCategory.BASE, value=0),
        Skill(name="Intimidation", category=SkillCategory.BASE, value=0),
        Skill(name="Investigation", category=SkillCategory.BASE, value=0),
        Skill(name="Medicine", category=SkillCategory.BASE, value=0),
        Skill(name="Nature", category=SkillCategory.BASE, value=0),
        Skill(name="Perception", category=SkillCategory.BASE, value=0),
        Skill(name="Performance", category=SkillCategory.BASE, value=0),
        Skill(name="Persuasion", category=SkillCategory.BASE, value=0),
        Skill(name="Religion", category=SkillCategory.BASE, value=0),
        Skill(name="Sleight of Hand", category=SkillCategory.BASE, value=0),
        Skill(name="Stealth", category=SkillCategory.BASE, value=0),
        Skill(name="Survival", category=SkillCategory.BASE, value=0),
    ],
    abilities=[
        Ability(name="to be specified", category=AbilityCategory.FEAT),
    ],
)
