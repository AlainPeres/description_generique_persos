"""
D&D 5th edition: system-specific block and derived values, the DnDCharacter
class, and the generic character template.

Default values ("to be specified", ability scores of 10) are meant to be
replaced when describing an actual character.
"""

from pydantic import Field
from typing import Annotated, Literal

from models import CharacterBase, Attribute, AttributeCategory, Skill, SkillCategory, Ability, AbilityCategory
from strict_model import StrictModel
from systems.common import SpellLevel, Remaining, DerivedValue, fixed, CharacterClass, DnDAbility


# ---------------------------------------------------------------------------
# System-specific block: Dungeons & Dragons 5e
# ---------------------------------------------------------------------------
DND_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Total Level", computed_from="sum of class levels"),
    DerivedValue(name="Current Ability Scores", applies_to=AttributeCategory.MAIN, computed_from="score - ability reduction"),
    DerivedValue(name="Ability Modifiers", applies_to=AttributeCategory.MAIN, computed_from="(current score - 10) // 2"),
    DerivedValue(name="Proficiency Bonus", computed_from="2 + (total level - 1) // 4"),
    DerivedValue(name="Skill Bonuses", applies_to="skill",
                 computed_from="ability modifier + proficiency level x proficiency bonus + other bonuses"),
    DerivedValue(name="Saving Throw Bonuses", applies_to=AttributeCategory.MAIN,
                 computed_from="ability modifier + proficiency bonus if proficient + other bonuses"),
    DerivedValue(name="Armor Class",
                 computed_from="armor, shield, Dexterity, class features, race, items, active spells"),
    DerivedValue(name="Initiative", computed_from="Dexterity modifier + other bonuses"),
    DerivedValue(name="Passive Perception", computed_from="10 + Perception bonus"),
    DerivedValue(name="Spell Save DC", computed_from="8 + proficiency bonus + spellcasting ability modifier"),
    DerivedValue(name="Spell Attack Bonus", computed_from="proficiency bonus + spellcasting ability modifier"),
    DerivedValue(name="Spell Slots (maximum)", computed_from="class levels, multiclass spellcaster table"),
    DerivedValue(name="Hit Dice (maximum)", computed_from="one per class level, die size by class"),
)

class DnDClass(CharacterClass):
    subclass: str = ""        # e.g. "Battle Master"; empty before it is chosen

class SpecificValuesDnD(StrictModel):
    skill_value_meaning: Literal["proficiency level: 0 none, 1 proficient, 2 expertise"] = (
        "proficiency level: 0 none, 1 proficient, 2 expertise"
    )
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(DND_DERIVED)] = DND_DERIVED
    # One entry per class (several when multiclassing); the total level is
    # the sum of the class levels, so it is not stored
    classes: list[DnDClass]
    race: str                 # or species
    experience_points: int = 0
    alignment: str            # e.g. "Lawful Good"
    deity: str = ""           # empty = none; e.g. "Tyr", "Pelor" (depends on the setting)
    size: str | None = None   # e.g. "Medium"
    speed: dict[str, int] = Field(default_factory=dict)   # in feet, per mode: {"walk": 30, "fly": 60}
    languages: list[str] = Field(default_factory=list)
    # Saves are stored as proficiencies only; their bonus is derived
    saving_throw_proficiencies: list[str] = Field(default_factory=list)  # e.g. ["Strength", "Constitution"]
    # State between two rests
    exhaustion: int = 0
    # Points lost until a rest or a restoration (Shadow's Strength Drain,
    # Feeblemind...); scores in attributes stay permanent. e.g. {"Strength": 3}
    ability_reduction: dict[DnDAbility, Remaining] = Field(default_factory=dict)
    inspiration: bool = False
    hit_dice_remaining: int | None = None     # None = all available
    # Slots are shared by all classes; pact magic (warlock) is separate.
    # A missing level means all its slots are available, so a character
    # after a long rest has {}; a spent level is written as 0.
    # e.g. Wizard 5 after two Shields and two Fireballs: {1: 2, 3: 0}
    spell_slots_remaining: dict[SpellLevel, Remaining] = Field(default_factory=dict)
    pact_slots_remaining: int | None = None   # None = no warlock levels
    # Names of Spell abilities. Empty = every Spell
    # ability is available: only fill it for classes that know more spells
    # than they prepare, such as the wizard. Unlike PF1, casting a prepared
    # spell spends a slot, not the spell: every prepared spell stays
    # available while a slot of a high enough level remains.
    prepared_spells: list[str] = Field(default_factory=list)
    # Class resources, and spells cast once per rest without a slot (racial,
    # feat, Mystic Arcanum...), e.g. {"Ki": 3, "Hellish Rebuke (Infernal Legacy)": 1}
    resources_remaining: dict[str, Remaining] = Field(default_factory=dict)


class DnDCharacter(CharacterBase):
    system: Literal["dnd5e"]
    specific_values: SpecificValuesDnD


# ---------------------------------------------------------------------------
# Generic template
# ---------------------------------------------------------------------------
generic_dnd5e = DnDCharacter(
    system="dnd5e",
    name="Generic D&D 5e Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesDnD(
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
