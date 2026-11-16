"""
Pathfinder 1st edition: system-specific block and derived values, the PF1Character
class, and the generic character template.

Default values ("to be specified", ability scores of 10, no ranks) are meant
to be replaced when describing an actual character.
"""

from pydantic import Field
from typing import Annotated, Literal

from models import CharacterBase, Attribute, AttributeCategory, Skill, SkillCategory, Ability, AbilityCategory
from strict_model import StrictModel
from systems.common import SpellLevel, Remaining, DerivedValue, fixed, CharacterClass, DnDAbility


# ---------------------------------------------------------------------------
# System-specific block: Pathfinder 1st edition
# ---------------------------------------------------------------------------
PF1_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Total Level", computed_from="sum of class levels"),
    DerivedValue(name="Ability Modifiers", applies_to=AttributeCategory.MAIN,
                 computed_from="(score - drain - 10) // 2, minus 1 per 2 points of ability damage"),
    DerivedValue(name="Base Attack Bonus", computed_from="sum of class progressions"),
    DerivedValue(name="Saving Throws",
                 computed_from="sum of class base saves + ability modifier + other bonuses - negative levels"),
    DerivedValue(name="Skill Totals", applies_to="skill",
                 computed_from="ranks + ability modifier + 3 if class skill with at least 1 rank"
                               " + other bonuses - armor check penalty"),
    DerivedValue(name="Armor Class",
                 computed_from="10 + armor, shield, Dexterity (capped by armor), size, natural armor,"
                               " deflection, dodge and other bonuses"),
    DerivedValue(name="Touch Armor Class", computed_from="Armor Class without armor, shield and natural armor"),
    DerivedValue(name="Flat-Footed Armor Class", computed_from="Armor Class without Dexterity and dodge bonuses"),
    DerivedValue(name="Combat Maneuver Bonus", computed_from="BAB + Strength modifier + special size modifier"),
    DerivedValue(name="Combat Maneuver Defense",
                 computed_from="10 + BAB + Strength and Dexterity modifiers + special size modifier"),
    DerivedValue(name="Initiative", computed_from="Dexterity modifier + other bonuses"),
    DerivedValue(name="Spell Save DC", computed_from="10 + spell level + casting ability modifier"),
    DerivedValue(name="Spells per Day (maximum)",
                 computed_from="class level table + bonus spells from the casting ability"),
)

# One entry per prepared slot: the same spell prepared twice appears twice
class PreparedSpell(StrictModel):
    name: str
    level: int                # 0 = orison / cantrip
    cast: bool = False        # already used since it was prepared

class PF1Class(CharacterClass):
    archetypes: list[str] = Field(default_factory=list)  # PF1 allows several per class
    # Each class has its own spells per day. Spontaneous casters: a missing
    # level means all its spells per day are available, a spent level is 0.
    spells_remaining: dict[SpellLevel, Remaining] = Field(default_factory=dict)
    prepared_spells: list[PreparedSpell] = Field(default_factory=list)          # prepared casters

class SpecificValuesPF1(StrictModel):
    skill_value_meaning: Literal["ranks"] = "ranks"
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(PF1_DERIVED)] = PF1_DERIVED
    # One entry per class; the total level is their sum, so it is not stored
    classes: list[PF1Class]
    favored_class: str = ""   # name of one of the classes
    race: str
    experience_points: int = 0
    alignment: str            # e.g. "Chaotic Neutral"
    deity: str = ""           # empty = none; e.g. "Iomedae", "Desna"
    size: str | None = None   # e.g. "Medium"
    speed: dict[str, int] = Field(default_factory=dict)   # in feet, per mode: {"land": 30, "swim": 15}
    languages: list[str] = Field(default_factory=list)
    # Class skills granted by traits; those from the class lists are derived
    additional_class_skills: list[str] = Field(default_factory=list)
    # Lasting states, e.g. {"Strength": 2}; same six abilities as D&D
    ability_damage: dict[DnDAbility, Remaining] = Field(default_factory=dict)
    ability_drain: dict[DnDAbility, Remaining] = Field(default_factory=dict)
    negative_levels: int = 0
    hero_points: int | None = None   # None = optional rule not used
    resources_remaining: dict[str, Remaining] = Field(default_factory=dict)  # e.g. {"Rage rounds": 5}


class PF1Character(CharacterBase):
    system: Literal["pf1"]
    specific_values: SpecificValuesPF1


# ---------------------------------------------------------------------------
# Generic template
# ---------------------------------------------------------------------------
generic_pf1 = PF1Character(
    system="pf1",
    name="Generic Pathfinder 1 Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesPF1(
        classes=[PF1Class(name="to be specified", level=1)],
        race="to be specified",
        alignment="to be specified",
        size="Medium",
        speed={"land": 30},
        languages=["Common"],
    ),
    attributes=[
        Attribute(name="Strength", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Dexterity", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Constitution", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Intelligence", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Wisdom", category=AttributeCategory.MAIN, value=10),
        Attribute(name="Charisma", category=AttributeCategory.MAIN, value=10),

        # Maximum HP is stored: it is rolled at each level. Armor Class (normal,
        # touch, flat-footed), BAB, saves, CMB, CMD and initiative are derived
        # (AC from armor, shield, Dexterity, size, natural armor, items and
        # spells), so they are not stored.
        Attribute(name="Maximum Hit Points", category=AttributeCategory.SECONDARY, value=10),
        Attribute(name="Current Hit Points", category=AttributeCategory.STATE, value=10),
        Attribute(name="Nonlethal Damage", category=AttributeCategory.STATE, value=0),
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
