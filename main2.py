"""
RPG character generation (multi-system) with Pydantic.

Architecture:
- A common base (Character) with two complementary layers:
  1. Generic layer: attributes, skills, abilities, spells, equipment
     (system-agnostic, usable across all RPGs)
  2. Optional system-specific block (specific_values: SpecificValuesDnD | SpecificValuesCthulhu | None)
     for systems whose structure cannot be expressed as name+value pairs
     (e.g. FATE Aspects, Stunts, Extras)
- All Character fields are optional (default to empty / None)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Any
import json


# ---------------------------------------------------------------------------
# System-specific block: Dungeons & Dragons 5e
# ---------------------------------------------------------------------------
class SpecificValuesDnD(BaseModel):
    system: Literal["dnd5e"]
    character_class: str
    race: str
    level: int
    alignment: str
    size: str | None = None
    speed: dict[str, int] = Field(default_factory=dict)
    languages: list[str] = Field(default_factory=list)
    reflex_save: int
    fortitude_save: int
    will_save: int


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
class SpecificValuesCthulhu(BaseModel):
    system: Literal["cthulhu6"]

# ---------------------------------------------------------------------------
# System-specific block: Fate
# ---------------------------------------------------------------------------
class SpecificValuesFate(BaseModel):
    system: Literal["fate"]
    Concept:str
    Aspects: list[str] = Field(default_factory=list)
    Stunts: list[str] = Field(default_factory=list)
    Extras: list[str] = Field(default_factory=list)
    FatePoints: int

# ---------------------------------------------------------------------------
# System-specific block: SagaS
# ---------------------------------------------------------------------------
class SpecificValuesSagas(BaseModel):
    system: Literal["SagaS"]  
# ---------------------------------------------------------------------------
#Utility Classes: common to large number of systems
# ---------------------------------------------------------------------------

class ItemCategory(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ITEM = "item"
    CONSUMABLE = "consumable"
 
 
class EquipmentItem(BaseModel):
    name: str
    category: ItemCategory
    quantity: int = Field(default=1, ge=1)
    weight: float | None = None  # in kg
    equipped: bool = False
    description: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)

class AbilityCategory(str, Enum):
    FEAT = "Feat"
    ORIGIN_ABILITY = "Origin Ability"
    CLASS_ABILITY = "Class Ability"
    POWER = "Power"
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"

class Ability(BaseModel):
    name: str
    category: AbilityCategory   
    value: int

class SkillCategory(str, Enum):
    BASE = "Base"
    NEW = "New"
    GENERIC = "Generic"
    SPECIALIZATION = "Specialization"

class Skill(BaseModel):
    name: str
    category: SkillCategory   
    value: int 

class Attribute(BaseModel):
    name: str      
    value: int 

class SpellCategory(str, Enum):
    BASE = "Base"
    NEW = "New"
   
class Spell(BaseModel):
    name: str
    category: SpellCategory  
    
    
# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(BaseModel):
    specific_values: SpecificValuesDnD | SpecificValuesCthulhu | SpecificValuesFate | SpecificValuesSagas | None = None
    name: str = ""
    description: str = ""
    occupation: str = ""
    background: str = ""    
    attributes: list[Attribute] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    abilities: list[Ability] = Field(default_factory=list)   
    spells: list[Spell] = Field(default_factory=list)
    equipment: list[EquipmentItem] = Field(default_factory=list)  

# ---------------------------------------------------------------------------
# Character creation
# ---------------------------------------------------------------------------
generic_dnd5e = Character(
    name="Generic D&D 5e Character",
    description="A generic adventurer in the world of Dungeons & Dragons 5th Edition",
    background="background not specified",
    specific_values=SpecificValuesDnD(
        system="dnd5e",
        character_class="to be specified",
        race="to be specified",
        level=1,
        alignment="to be specified",
        size="Medium",
        speed={"walk": 25},
        languages=["Common"],
        reflex_save=10,
        fortitude_save=10,
        will_save=10,       
    ),
    attributes=[
        Attribute(name="Strength", value=10),
        Attribute(name="Dexterity", value=10),
        Attribute(name="Constitution", value=10),
        Attribute(name="Intelligence", value=10),
        Attribute(name="Wisdom", value=10),
        Attribute(name="Charisma", value=10),
        Attribute(name="Armor Class", value=10),
        Attribute(name="Hit Points", value=10),
    ],
    skills=[
        Skill(name="Acrobatics", category=SkillCategory.BASE, value=10),
        Skill(name="Animal Handling", category=SkillCategory.BASE, value=10),
        Skill(name="Arcana", category=SkillCategory.BASE, value=10),
        Skill(name="Athletics", category=SkillCategory.BASE, value=10),
        Skill(name="Deception", category=SkillCategory.BASE, value=10),
        Skill(name="History", category=SkillCategory.BASE, value=10),
        Skill(name="Insight", category=SkillCategory.BASE, value=10),
        Skill(name="Intimidation", category=SkillCategory.BASE, value=10),
        Skill(name="Investigation", category=SkillCategory.BASE, value=10),
        Skill(name="Medicine", category=SkillCategory.BASE, value=10),
        Skill(name="Nature", category=SkillCategory.BASE, value=10),
        Skill(name="Perception", category=SkillCategory.BASE, value=10),
        Skill(name="Performance", category=SkillCategory.BASE, value=10),
        Skill(name="Persuasion", category=SkillCategory.BASE, value=10),
        Skill(name="Religion", category=SkillCategory.BASE, value=10),
        Skill(name="Sleight of Hand", category=SkillCategory.BASE, value=10),
        Skill(name="Stealth", category=SkillCategory.BASE, value=10),
        Skill(name="Survival", category=SkillCategory.BASE, value=10),
    ],
    abilities=[
        Ability(name="to be specified", category=AbilityCategory.FEAT, value=1),       
    ],
)

generic_cthulhu6 = Character(
    name="Generic Cthulhu 6 Character",
    description="to be specified",
    background="to be specified",
    occupation="to be specified",
    specific_values=SpecificValuesCthulhu(system="cthulhu6"),
    attributes=[
        Attribute(name="Strength", value=10),        
        Attribute(name="Constitution", value=10),
        Attribute(name="Size", value=10),
        Attribute(name="Dexterity", value=10),             
        Attribute(name="Appearance", value=10),
        Attribute(name="Intelligence", value=10),
        Attribute(name="Power", value=10),
        Attribute(name="Education", value=10),
        Attribute(name="Sanity", value=10),
        Attribute(name="Hit Points", value=10),
        Attribute(name="Magic Points", value=10),
        Attribute(name="Move", value=10),
    ],
    skills=[
        Skill(name="Accounting", category=SkillCategory.BASE, value=10),
        Skill(name="Anthropology", category=SkillCategory.BASE, value=1),
        Skill(name="Archaeology", category=SkillCategory.BASE, value=1),
        Skill(name="Art", category=SkillCategory.GENERIC, value=5),
        Skill(name="Astronomy", category=SkillCategory.BASE, value=1),
        Skill(name="Bargain", category=SkillCategory.BASE, value=5),
        Skill(name="Biology", category=SkillCategory.BASE, value=1),
        Skill(name="Chemistry", category=SkillCategory.BASE, value=1),
        Skill(name="Climb", category=SkillCategory.BASE, value=40),
        Skill(name="Computer Use", category=SkillCategory.BASE, value=1),
        Skill(name="Conceal", category=SkillCategory.BASE, value=15),
        Skill(name="Craft", category=SkillCategory.GENERIC, value=5),
        Skill(name="Credit Rating", category=SkillCategory.BASE, value=15),
        Skill(name="Cthulhu Mythos", category=SkillCategory.BASE, value=0),
        Skill(name="Disguise", category=SkillCategory.BASE, value=1),
        Skill(name="Dodge", category=SkillCategory.BASE, value=20),
        Skill(name="Drive Auto", category=SkillCategory.BASE, value=20),
        Skill(name="Electr. Repair", category=SkillCategory.BASE, value=10),
        Skill(name="Electronics", category=SkillCategory.BASE, value=1),
        Skill(name="Fast Talk", category=SkillCategory.BASE, value=5),
        Skill(name="First Aid", category=SkillCategory.BASE, value=30),
        Skill(name="Geology", category=SkillCategory.BASE, value=1),
        Skill(name="Hide", category=SkillCategory.BASE, value=10),
        Skill(name="History", category=SkillCategory.BASE, value=20),
        Skill(name="Jump", category=SkillCategory.BASE, value=25),
        Skill(name="Law", category=SkillCategory.BASE, value=5),
        Skill(name="Library Use", category=SkillCategory.BASE, value=25),
        Skill(name="Listen", category=SkillCategory.BASE, value=25),
        Skill(name="Locksmith", category=SkillCategory.BASE, value=1),
        Skill(name="Martial Arts", category=SkillCategory.BASE, value=1),
        Skill(name="Mech. Repair", category=SkillCategory.BASE, value=20),
        Skill(name="Medicine", category=SkillCategory.BASE, value=5),
        Skill(name="Natural History", category=SkillCategory.BASE, value=10),
        Skill(name="Navigate", category=SkillCategory.BASE, value=10),
        Skill(name="Occult", category=SkillCategory.BASE, value=5),
        Skill(name="Opr. Hvy. Mch.", category=SkillCategory.BASE, value=1),
        Skill(name="Other Languages", category=SkillCategory.GENERIC, value=1),
        Skill(name="Own Language", category=SkillCategory.BASE, value=50),
        Skill(name="Persuade", category=SkillCategory.BASE, value=15),
        Skill(name="Pharmacy", category=SkillCategory.BASE, value=1),
        Skill(name="Photography", category=SkillCategory.BASE, value=10),
        Skill(name="Physics", category=SkillCategory.BASE, value=1),
        Skill(name="Pilot", category=SkillCategory.GENERIC, value=1),
        Skill(name="Psychoanalysis", category=SkillCategory.BASE, value=1),
        Skill(name="Psychology", category=SkillCategory.BASE, value=5),
        Skill(name="Ride", category=SkillCategory.BASE, value=5),
        Skill(name="Sneak", category=SkillCategory.BASE, value=10),
        Skill(name="Spot Hidden", category=SkillCategory.BASE, value=25),
        Skill(name="Swim", category=SkillCategory.BASE, value=25),
        Skill(name="Throw", category=SkillCategory.BASE, value=25),
        Skill(name="Track", category=SkillCategory.BASE, value=10),
        Skill(name="Handgun", category=SkillCategory.BASE, value=20),
        Skill(name="Machine Gun", category=SkillCategory.BASE, value=15),
        Skill(name="Rifle", category=SkillCategory.BASE, value=25),
        Skill(name="Shotgun", category=SkillCategory.BASE, value=30),
        Skill(name="SMG", category=SkillCategory.BASE, value=15),
        Skill(name="Fist", category=SkillCategory.BASE, value=50),
        Skill(name="Grapple", category=SkillCategory.BASE, value=25),
        Skill(name="Head", category=SkillCategory.BASE, value=10),
        Skill(name="Kick", category=SkillCategory.BASE, value=25),
    ],
)


# ---------------------------------------------------------------------------
# Display: generated JSON + global JSON Schema
# ---------------------------------------------------------------------------
def print_separator(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def export_json(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  -> exported: {path}")


if __name__ == "__main__":
    print_separator("D&D 5e CHARACTER (generated JSON)")
    print(generic_dnd5e.model_dump_json(indent=2))

    print_separator("CTHULHU CHARACTER (generated JSON)")
    print(generic_cthulhu6.model_dump_json(indent=2))

    print_separator("JSON SCHEMA (common to both systems)")
    print(json.dumps(Character.model_json_schema(), indent=2, ensure_ascii=False))

    print_separator("JSON FILE EXPORT")
    export_json("generic_dnd5e.json", generic_dnd5e.model_dump_json(indent=2))
    export_json("generic_cthulhu6.json", generic_cthulhu6.model_dump_json(indent=2))
    export_json("schema_character.json", json.dumps(Character.model_json_schema(), indent=2, ensure_ascii=False))

    print_separator("VALIDATION: reload from raw JSON")
    raw = generic_dnd5e.model_dump_json()
    reloaded = Character.model_validate_json(raw)
    system = reloaded.specific_values.system if reloaded.specific_values else "no system"
    print(f"Reloaded character: {reloaded.name} ({system})")

    print_separator("VALIDATION: error on inconsistent data")
    try:
        Character(
            name="Test",
            player="X",
            specific_values={"system": "dnd5e", "character_class": "Mage"},  # missing fields
        )
    except Exception as e:
        print(f"Error detected as expected:\n{e}")
