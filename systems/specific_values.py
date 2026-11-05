"""
System-specific value blocks, one per RPG system.

Kept separate from models.py so that models.py can import the
SpecificValues union without each system module having to import
Character (which would create a circular import, since
systems/<game>.py modules import Character to build their generic
character templates).

To add a new system: define its SpecificValuesXxx(StrictModel) class
here (with a `system: Literal[...]` discriminator field) and add it
to the SpecificValues union at the bottom of this file.
"""

from pydantic import AfterValidator, Field, field_validator
from typing import Annotated, Literal

from strict_model import StrictModel

# Conventions shared by every block:
# - `system` is a single-value Literal: it tells Pydantic which block to use
#   (see the SpecificValues union at the bottom of this file);
# - every block whose system has skills declares `skill_value_meaning`: the
#   meaning of Skill.value is a fixed convention per system, written in each
#   JSON so the file explains itself; any other value is rejected;
# - only what remains is stored: maximums (slots per level, uses per day)
#   are derived. These two types carry the matching bounds.
SpellLevel = Annotated[int, Field(ge=1, le=9)]
Remaining = Annotated[int, Field(ge=0)]


# ---------------------------------------------------------------------------
# Derived values: not stored, computed outside the model. Each system lists
# them in a fixed `derived_values` field, so that a reader of the JSON knows
# what exists and the external calculator knows what to produce.
# ---------------------------------------------------------------------------
class DerivedValue(StrictModel):
    name: str                 # e.g. "Armor Class"
    computed_from: str        # sources or formula, for the reader and the calculator


# Same behavior as a single-value Literal, for values Literal cannot hold
# (lists, models): the field has a default and any other value is rejected
def fixed[T](expected: T) -> AfterValidator:
    def check(value: T) -> T:
        if value != expected:
            raise ValueError("fixed by the system; do not edit")
        return value
    return AfterValidator(check)


# ---------------------------------------------------------------------------
# Character classes: common base of the class-based systems (D&D, PF1), each
# system adding its own fields
# ---------------------------------------------------------------------------
class CharacterClass(StrictModel):
    name: str                 # e.g. "Fighter"
    level: int = Field(ge=1, le=20)

# A class taken again is a higher level, not a new entry. Names are compared
# without case or surrounding spaces ("Fighter" = " fighter").
def check_unique_class_names[C: CharacterClass](classes: list[C]) -> list[C]:
    names = [c.name.strip().casefold() for c in classes]
    if len(names) != len(set(names)):
        raise ValueError("each class must appear only once; raise its level instead")
    return classes

# ---------------------------------------------------------------------------
# System-specific block: No Rules
# ---------------------------------------------------------------------------
class SpecificValuesNoRules(StrictModel):
    system: Literal["norules"]
    tags: list[str] = Field(default_factory=list)   # free descriptors: "brave", "noble"...


# ---------------------------------------------------------------------------
# System-specific block: Dungeons & Dragons 5e
# ---------------------------------------------------------------------------
DND_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Total Level", computed_from="sum of class levels"),
    DerivedValue(name="Current Ability Scores", computed_from="score - ability reduction"),
    DerivedValue(name="Ability Modifiers", computed_from="(current score - 10) // 2"),
    DerivedValue(name="Proficiency Bonus", computed_from="2 + (total level - 1) // 4"),
    DerivedValue(name="Skill Bonuses",
                 computed_from="ability modifier + proficiency level x proficiency bonus + other bonuses"),
    DerivedValue(name="Saving Throw Bonuses",
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

DnDAbility = Literal["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

class DnDClass(CharacterClass):
    subclass: str = ""        # e.g. "Battle Master"; empty before it is chosen

class SpecificValuesDnD(StrictModel):
    system: Literal["dnd5e"]
    skill_value_meaning: Literal["proficiency level: 0 none, 1 proficient, 2 expertise"] = (
        "proficiency level: 0 none, 1 proficient, 2 expertise"
    )
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(DND_DERIVED)] = DND_DERIVED
    # One entry per class (several when multiclassing); the total level is
    # the sum of the class levels, so it is not stored
    classes: list[DnDClass] = Field(min_length=1)
    race: str                 # or species
    experience_points: int = Field(default=0, ge=0)
    alignment: str            # e.g. "Lawful Good"
    deity: str = ""           # empty = none; e.g. "Tyr", "Pelor" (depends on the setting)
    size: str | None = None   # e.g. "Medium"
    speed: dict[str, int] = Field(default_factory=dict)   # in feet, per mode: {"walk": 30, "fly": 60}
    languages: list[str] = Field(default_factory=list)
    # Saves are stored as proficiencies only; their bonus is derived
    saving_throw_proficiencies: list[str] = Field(default_factory=list)  # e.g. ["Strength", "Constitution"]
    # State between two rests
    exhaustion: int = Field(default=0, ge=0, le=6)
    # Points lost until a rest or a restoration (Shadow's Strength Drain,
    # Feeblemind...); scores in attributes stay permanent. e.g. {"Strength": 3}
    ability_reduction: dict[DnDAbility, Remaining] = Field(default_factory=dict)
    inspiration: bool = False
    hit_dice_remaining: int | None = Field(default=None, ge=0)     # None = all available
    # Slots are shared by all classes; pact magic (warlock) is separate.
    # A missing level means all its slots are available, so a character
    # after a long rest has {}; a spent level is written as 0.
    # e.g. Wizard 5 after two Shields and two Fireballs: {1: 2, 3: 0}
    spell_slots_remaining: dict[SpellLevel, Remaining] = Field(default_factory=dict)
    pact_slots_remaining: int | None = Field(default=None, ge=0)   # None = no warlock levels
    # Names of Spell abilities (checked by Character). Empty = every Spell
    # ability is available: only fill it for classes that know more spells
    # than they prepare, such as the wizard. Unlike PF1, casting a prepared
    # spell spends a slot, not the spell: every prepared spell stays
    # available while a slot of a high enough level remains.
    prepared_spells: list[str] = Field(default_factory=list)
    # Class resources, and spells cast once per rest without a slot (racial,
    # feat, Mystic Arcanum...), e.g. {"Ki": 3, "Hellish Rebuke (Infernal Legacy)": 1}
    resources_remaining: dict[str, Remaining] = Field(default_factory=dict)

    @field_validator("classes")
    @classmethod
    def no_duplicate_class(cls, classes: list[DnDClass]) -> list[DnDClass]:
        return check_unique_class_names(classes)



# ---------------------------------------------------------------------------
# System-specific block: Pathfinder 1st edition
# ---------------------------------------------------------------------------
PF1_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Total Level", computed_from="sum of class levels"),
    DerivedValue(name="Ability Modifiers",
                 computed_from="(score - drain - 10) // 2, minus 1 per 2 points of ability damage"),
    DerivedValue(name="Base Attack Bonus", computed_from="sum of class progressions"),
    DerivedValue(name="Saving Throws",
                 computed_from="sum of class base saves + ability modifier + other bonuses - negative levels"),
    DerivedValue(name="Skill Totals",
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
    level: int = Field(ge=0, le=9)   # 0 = orison / cantrip
    cast: bool = False        # already used since it was prepared

class PF1Class(CharacterClass):
    archetypes: list[str] = Field(default_factory=list)  # PF1 allows several per class
    # Each class has its own spells per day. Spontaneous casters: a missing
    # level means all its spells per day are available, a spent level is 0.
    spells_remaining: dict[SpellLevel, Remaining] = Field(default_factory=dict)
    prepared_spells: list[PreparedSpell] = Field(default_factory=list)          # prepared casters

class SpecificValuesPF1(StrictModel):
    system: Literal["pf1"]
    skill_value_meaning: Literal["ranks"] = "ranks"
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(PF1_DERIVED)] = PF1_DERIVED
    # One entry per class; the total level is their sum, so it is not stored
    classes: list[PF1Class] = Field(min_length=1)
    favored_class: str = ""   # name of one of the classes
    race: str
    experience_points: int = Field(default=0, ge=0)
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
    negative_levels: int = Field(default=0, ge=0)
    hero_points: int | None = Field(default=None, ge=0)   # None = optional rule not used
    resources_remaining: dict[str, Remaining] = Field(default_factory=dict)  # e.g. {"Rage rounds": 5}

    @field_validator("classes")
    @classmethod
    def no_duplicate_class(cls, classes: list[PF1Class]) -> list[PF1Class]:
        return check_unique_class_names(classes)


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
    system: Literal["cthulhu6"]
    skill_value_meaning: Literal["percentage"] = "percentage"
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(CTHULHU_DERIVED)] = CTHULHU_DERIVED
    # Everything else lives in the generic layer: characteristics, current
    # Sanity, skills and their improvement checks, and mental disorders
    # (Character.conditions, kind Mental, duration temporary / indefinite /
    # permanent)


# ---------------------------------------------------------------------------
# System-specific block: Fate
# ---------------------------------------------------------------------------
# `available` (StressBox and Consequence) starts from Physique / Will in Fate
# Core, but stunts, extras or off-rules decisions can change it in ways no
# calculator can foresee: it is not derivable, so it is stored
class StressBox(StrictModel):
    available: bool = True    # the box exists for this character
    checked: bool = False     # the box is ticked

class Consequence(StrictModel):
    available: bool = True    # the slot exists for this character
    value: int                # stress absorbed: 2, 4, 6 or 8 depending on severity
    text: str = ""            # the consequence suffered, e.g. "Broken arm"

class SpecificValuesFate(StrictModel):
    system: Literal["fate"]
    skill_value_meaning: Literal["rating on the Fate ladder"] = "rating on the Fate ladder"
    HighConcept: str          # main aspect: who the character is
    Trouble: str              # aspect that gets the character into trouble
    Aspects: list[str] = Field(default_factory=list, max_length=3)  # the other aspects
    Extras: list[str] = Field(default_factory=list)   # gear, allies, powers given as aspects
    FatePoints: int           # current points
    Refresh: int              # points restored at the start of a session
    # Stress tracks, keyed by box name ("Box 1" to "Box 4")
    PhysicalStress: dict[str, StressBox] = Field(default_factory=dict, max_length=4)
    MentalStress: dict[str, StressBox] = Field(default_factory=dict, max_length=4)
    # Keyed by slot name ("Mild", "Moderate", "Severe", "Extreme", "Mild Physical"...)
    Consequences: dict[str, Consequence] = Field(default_factory=dict, max_length=6)

# ---------------------------------------------------------------------------
# System-specific block: SagaS
# ---------------------------------------------------------------------------
# Attributes a skill can be based on: the 8 main and the 4 secondary ones.
# Used by Character to check the attribute of skills created by the player.
SAGAS_SKILL_ATTRIBUTES: tuple[str, ...] = (
    "Strength", "Agility", "Endurance", "Dexterity",
    "Wit", "Will", "Presence", "Instinct",
    "Initiative", "Close Combat", "Ranged Combat", "Speed",
)

SAGAS_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Skill Levels", computed_from="associated attribute + learning level"),
    DerivedValue(name="Protection",
                 computed_from="Armor + Abilities (super powers, outside the base rules); 0 by default"),
    DerivedValue(name="MaxImpactBonus", computed_from="2*Protection + Physical Shock Threshold"),
    DerivedValue(name="Physical Hit Points", computed_from="2*(Strength + Will + Endurance)"),
    DerivedValue(name="Psychical Hit Points", computed_from="2*(Presence + Will + Instinct)"),
    DerivedValue(name="Physical Shock Threshold", computed_from="10 + UT Strength bonus"),
    DerivedValue(name="Psychical Shock Threshold", computed_from="10 + UT Presence bonus"),
    DerivedValue(name="Reflex Defense", computed_from="2 + Dodge skill level / 2, rounded down"),
)

class SpecificValuesSagas(StrictModel):
    system: Literal["sagas"]
    # The skill level (associated attribute + learning level) is derived;
    # the attribute associated with each skill is fixed by the rules
    skill_value_meaning: Literal["learning level"] = "learning level"
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(SAGAS_DERIVED)] = SAGAS_DERIVED
    unspent_creation_points: int = Field(default=0, ge=0)  # set aside for later
    # Current wounds and stun are attributes; serious injuries are
    # Character.conditions, kind Physical, or kind Mental for psychical ones


# ---------------------------------------------------------------------------
# System-specific block: Daredevils (FGU)
# ---------------------------------------------------------------------------
# Used by Character to check the attribute and talent of skills added by the
# GM, and as the keys of the attribute dictionaries below
DAREDEVILS_ATTRIBUTES: tuple[str, ...] = ("Wit", "Will", "Strength", "Deftness", "Speed", "Health")
DAREDEVILS_TALENTS: tuple[str, ...] = (
    "Charismatic", "Combative", "Communicative", "Esthetic", "Mechanical", "Natural", "Scientific",
)
DaredevilsAttribute = Literal["Wit", "Will", "Strength", "Deftness", "Speed", "Health"]

# Unless stated otherwise, Daredevils rounds to the nearest (3.5 rounds up)
DAREDEVILS_DERIVED: tuple[DerivedValue, ...] = (
    DerivedValue(name="Current Attributes",
                 computed_from="permanent value - attribute_loss; Deftness and Speed -50% when Seriously Wounded"),
    DerivedValue(name="Attribute Groups and Effect Dice", computed_from="current value, Attribute Group Chart"),
    DerivedValue(name="Attribute Saving Throws", computed_from="current value / 2, rounded down"),
    DerivedValue(name="Critical Saving Throws", computed_from="current value / 3, rounded down"),
    DerivedValue(name="Basic Chance of Success", computed_from="skill score / 5, rounded down"),
    DerivedValue(name="Combat Dodge Ability", computed_from="(current Deftness Group + current Speed Group) / 2"),
    DerivedValue(name="Weapon Defense Ability", computed_from="hand-to-hand BCS / 4"),
    DerivedValue(name="Damage Resistance Total", computed_from="permanent Health + Strength + Will"),
    DerivedValue(name="Seriously Wounded", computed_from="Lethal + Subdual Damage > Damage Resistance Total / 2"),
    DerivedValue(name="Encumbrance Capacity", computed_from="5 + Strength Attribute Saving Throw, in kg"),
    DerivedValue(name="Freely Improvable Skills Quota", computed_from="current Wit + current Will"),
    DerivedValue(name="Learning Rate", computed_from="Wit Group"),
    DerivedValue(name="Shock Factor", computed_from="10 + Health Group"),
    DerivedValue(name="Size", computed_from="height and weight category, Physical Aspects Chart"),
)

class SpecificValuesDaredevils(StrictModel):
    system: Literal["daredevils"]
    skill_value_meaning: Literal["score (0 or more); BCS = score / 5, rounded down"] = (
        "score (0 or more); BCS = score / 5, rounded down"
    )
    derived_values: Annotated[tuple[DerivedValue, ...], fixed(DAREDEVILS_DERIVED)] = DAREDEVILS_DERIVED
    # Attribute points lost to wounds, disease...; the current value is
    # derived from the permanent one (the Attribute), e.g. {"Deftness": 3}
    attribute_loss: dict[DaredevilsAttribute, Remaining] = Field(default_factory=dict)
    # Optional rule 1.8.5b: +0.5 to the governing attribute per BCS point
    # gained; fractions toward the next full point, e.g. {"Deftness": 0.5}
    attribute_progress: dict[DaredevilsAttribute, Annotated[float, Field(ge=0, lt=1)]] = Field(
        default_factory=dict)
    favored_hand: Literal["right", "left"] = "right"
    # Physical characteristics
    height: str = ""                     # e.g. "5'4\""
    weight_kg: int | None = Field(default=None, ge=0)
    looks: Literal["Ugly", "Homely", "Mediocre", "Average",
                   "Good Looking", "Comely", "Handsome"] = "Average"
    # Advanced rule: names of the designated skills (checked by Character)
    freely_improvable_skills: list[str] = Field(default_factory=list)
    # The hero; finances, degrees, rank, record, licenses and contacts go in
    # Character.background
    motivation: str = ""                 # e.g. Revenge, Altruism, Challenge, Work
    method: str = ""                     # e.g. Vigilante, Lawman, Man of Mystery, Mastermind, Sidekick
    code: str = ""                       # personal code of conduct


# ---------------------------------------------------------------------------
# Registry: every system-specific class must be listed here to be usable
# as Character.specific_values. Written out explicitly so that type checkers
# (Pylance, mypy) know each member. `discriminator="system"` lets Pydantic
# pick the right subtype directly from the `system` field instead of trying
# each member in turn.
# ---------------------------------------------------------------------------
SpecificValues = Annotated[
    SpecificValuesDnD
    | SpecificValuesPF1
    | SpecificValuesCthulhu
    | SpecificValuesFate
    | SpecificValuesSagas
    | SpecificValuesDaredevils
    | SpecificValuesNoRules,
    Field(discriminator="system"),
]
