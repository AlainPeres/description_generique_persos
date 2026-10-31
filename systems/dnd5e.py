from models import Character, Attribute, Skill, SkillCategory, Ability, AbilityCategory
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
        Attribute(name="Strength", value=10),
        Attribute(name="Dexterity", value=10),
        Attribute(name="Constitution", value=10),
        Attribute(name="Intelligence", value=10),
        Attribute(name="Wisdom", value=10),
        Attribute(name="Charisma", value=10),

        Attribute(name="Armor Class", value=10),
        Attribute(name="Maximum Hit Points", value=10),
        Attribute(name="Current Hit Points", value=10),
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
