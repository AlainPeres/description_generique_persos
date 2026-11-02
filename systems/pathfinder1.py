"""
Generic Pathfinder 1st edition character template.

Default values ("to be specified", ability scores of 10, no ranks) are meant
to be replaced when describing an actual character.
"""

from models import Character, Attribute, Skill, SkillCategory, Ability, AbilityCategory
from systems.specific_values import SpecificValuesPF1, PF1Class

generic_pf1 = Character(
    name="Generic Pathfinder 1 Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesPF1(
        system="pf1",
        classes=[PF1Class(name="to be specified", level=1)],
        race="to be specified",
        alignment="to be specified",
        size="Medium",
        speed={"land": 30},
        languages=["Common"],
    ),
    attributes=[
        Attribute(name="Strength", value=10),
        Attribute(name="Dexterity", value=10),
        Attribute(name="Constitution", value=10),
        Attribute(name="Intelligence", value=10),
        Attribute(name="Wisdom", value=10),
        Attribute(name="Charisma", value=10),

        # Maximum HP is stored: it is rolled at each level. Armor Class (normal,
        # touch, flat-footed), BAB, saves, CMB, CMD and initiative are derived
        # (AC from armor, shield, Dexterity, size, natural armor, items and
        # spells), so they are not stored.
        Attribute(name="Maximum Hit Points", value=10),
        Attribute(name="Current Hit Points", value=10),
        Attribute(name="Nonlethal Damage", value=0),
    ],
    # Skill value = ranks; the total bonus (ability modifier, +3 class skill,
    # feats, items, armor check penalty...) is derived from them
    skills=[
        Skill(name="Acrobatics", category=SkillCategory.BASE, value=0),
        Skill(name="Appraise", category=SkillCategory.BASE, value=0),
        Skill(name="Bluff", category=SkillCategory.BASE, value=0),
        Skill(name="Climb", category=SkillCategory.BASE, value=0),
        # Craft, Perform and Profession are open-ended: "Craft (Weapons)"...
        Skill(name="Craft", category=SkillCategory.GENERIC, value=0),
        Skill(name="Diplomacy", category=SkillCategory.BASE, value=0),
        Skill(name="Disable Device", category=SkillCategory.BASE, value=0),
        Skill(name="Disguise", category=SkillCategory.BASE, value=0),
        Skill(name="Escape Artist", category=SkillCategory.BASE, value=0),
        Skill(name="Fly", category=SkillCategory.BASE, value=0),
        Skill(name="Handle Animal", category=SkillCategory.BASE, value=0),
        Skill(name="Heal", category=SkillCategory.BASE, value=0),
        Skill(name="Intimidate", category=SkillCategory.BASE, value=0),
        # The ten Knowledge skills form a closed list, hence BASE
        Skill(name="Knowledge (Arcana)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Dungeoneering)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Engineering)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Geography)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (History)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Local)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Nature)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Nobility)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Planes)", category=SkillCategory.BASE, value=0),
        Skill(name="Knowledge (Religion)", category=SkillCategory.BASE, value=0),
        Skill(name="Linguistics", category=SkillCategory.BASE, value=0),
        Skill(name="Perception", category=SkillCategory.BASE, value=0),
        Skill(name="Perform", category=SkillCategory.GENERIC, value=0),
        Skill(name="Profession", category=SkillCategory.GENERIC, value=0),
        Skill(name="Ride", category=SkillCategory.BASE, value=0),
        Skill(name="Sense Motive", category=SkillCategory.BASE, value=0),
        Skill(name="Sleight of Hand", category=SkillCategory.BASE, value=0),
        Skill(name="Spellcraft", category=SkillCategory.BASE, value=0),
        Skill(name="Stealth", category=SkillCategory.BASE, value=0),
        Skill(name="Survival", category=SkillCategory.BASE, value=0),
        Skill(name="Swim", category=SkillCategory.BASE, value=0),
        Skill(name="Use Magic Device", category=SkillCategory.BASE, value=0),
    ],
    abilities=[
        Ability(name="to be specified", category=AbilityCategory.FEAT),
    ],
)
