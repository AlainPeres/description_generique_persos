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
    movement: dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
class SpecificValuesCthulhu(BaseModel):
    system: Literal["cthulhu"]

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
# System-specific block: Fate
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
thorin = Character(
    name="Thorin Ironforge",
    description="Muscular dwarf with a long beard and a hammer",
    background="Dwarf blacksmith exiled from his mountain",
    specific_values=SpecificValuesDnD(
        system="dnd5e",
        character_class="Fighter",
        race="Dwarf",
        level=3,
        alignment="Lawful Good",
        size="Medium",
        movement={"walk": 25},
    ),
    attributes=[
        Attribute(name="Strength", value=16),
        Attribute(name="Dexterity", value=12),
        Attribute(name="Constitution", value=15),
        Attribute(name="Intelligence", value=10),
        Attribute(name="Wisdom", value=11),
        Attribute(name="Charisma", value=8),
        Attribute(name="Armor Class", value=17),
        Attribute(name="Hit Points", value=28),
    ],
    skills=[
        Skill(name="Climb", category=SkillCategory.BASE, value=30),
    ],
    abilities=[
        Ability(name="Action Surge", category=AbilityCategory.FEAT, value=1),
        Ability(name="Second Wind", category=AbilityCategory.FEAT, value=1),
    ],
)

eleanor = Character(
    name="Eleanor Whitfield",
    description="50 years old, blond hair, green eyes",
    background="Librarian in Arkham",
    occupation="Librarian",
    specific_values=SpecificValuesCthulhu(system="cthulhu"),
    attributes=[
        Attribute(name="Strength", value=10),
        Attribute(name="Dexterity", value=12),
        Attribute(name="Constitution", value=14),
        Attribute(name="Size", value=10),
        Attribute(name="Intelligence", value=16),
        Attribute(name="Charisma", value=12),
        Attribute(name="Education", value=70),
        Attribute(name="Sanity", value=65),
        Attribute(name="Hit Points", value=11),
        Attribute(name="Move", value=8),
    ],
    skills=[
        Skill(name="Library Use", category=SkillCategory.BASE, value=70),
        Skill(name="Psychology", category=SkillCategory.BASE, value=45),
        Skill(name="Firearms", category=SkillCategory.BASE, value=25),
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
    print(thorin.model_dump_json(indent=2))

    print_separator("CTHULHU CHARACTER (generated JSON)")
    print(eleanor.model_dump_json(indent=2))

    print_separator("JSON SCHEMA (common to both systems)")
    print(json.dumps(Character.model_json_schema(), indent=2, ensure_ascii=False))

    print_separator("JSON FILE EXPORT")
    export_json("thorin.json", thorin.model_dump_json(indent=2))
    export_json("eleanor.json", eleanor.model_dump_json(indent=2))
    export_json("schema_character.json", json.dumps(Character.model_json_schema(), indent=2, ensure_ascii=False))

    print_separator("VALIDATION: reload from raw JSON")
    raw = eleanor.model_dump_json()
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
