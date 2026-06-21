"""
RPG character generation (multi-system) with Pydantic.

Architecture:
- A common base (Character) shared across all systems
- A system-specific "stats" block, automatically selected
  via a discriminated union on the "system" field
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
class StatsDnD(BaseModel):
    system: Literal["dnd5e"]
    character_class: str
    race: str
    level: int 
    alignment: str
    Strength: int 
    Dexterity: int 
    Constitution: int 
    Intelligence: int 
    Wisdom: int 
    Charisma: int 
    Armor_Class: int
    Hit_Points: int    
    size: str | None = None
    movement: dict[str, int] = Field(default_factory=dict)
    base_feats: list[str] = Field(default_factory=list)
    new_feats: list[str] = Field(default_factory=list)
    base_skills: dict[str, int] = Field(default_factory=dict)
    new_skills: dict[str, int] = Field(default_factory=dict)
    specialized_skills: dict[str, int] = Field(default_factory=dict)   
    base_spells: list[str] = Field(default_factory=list)
    new_spells: list[str] = Field(default_factory=list)
    origin_abilities: list[str] = Field(default_factory=list)
    class_abilities: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
class StatsCthulhu(BaseModel):
    system: Literal["cthulhu"]   
    Strength: int 
    Dexterity: int
    Constitution: int 
    Size: int 
    Intelligence: int 
    Charisma: int 
    Education: int    
    Sanity: int | None = None
    Hit_Points: int   
    Move:int
    base_skills: dict[str, int] = Field(default_factory=dict)
    new_skills: dict[str, int] = Field(default_factory=dict)
    specialized_skills: dict[str, int] = Field(default_factory=dict)
    base_spells: list[str] = Field(default_factory=list)
    new_spells: list[str] = Field(default_factory=list)

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
    
# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(BaseModel):
    name: str
    description: str = ""
    occupation: str = ""
    background: str = ""
    stats: StatsDnD | StatsCthulhu = Field(discriminator="system")
    equipment: list[EquipmentItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Character creation
# ---------------------------------------------------------------------------
thorin = Character(
    name="Thorin Ironforge",
    description="Muscular dwarf with a long beard and a hammer",
    background="Dwarf blacksmith exiled from his mountain",
    stats=StatsDnD(
        system="dnd5e",
        character_class="Fighter",
        race="Dwarf",
        alignment="Lawful Good",
        level=3,
        Strength=16,
        Dexterity=12,
        Constitution=15,
        Intelligence=10,
        Wisdom=11,
        Charisma=8,
        Armor_Class=17,
        Hit_Points=28,        
        base_feats=[],       
        base_skills={}      
    ),
)

eleanor = Character(
    name="Eleanor Whitfield",
    description="50 years old, blond hair, green eyes",
    background="Librarian in Arkham",  
    stats=StatsCthulhu(
        system="cthulhu",
        Strength=10,
        Dexterity=12,
        Constitution=14,
        Size=10,
        Intelligence=16,
        Charisma=12,
        Education=70,
        Sanity=65,
        Hit_Points=11,
        Move=8,
        base_skills={
            "Library Use": 70,
            "Psychology": 45,
            "Firearms": 25,
        },    
    ),
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
    print(f"Reloaded character: {reloaded.name} ({reloaded.stats.system})")

    print_separator("VALIDATION: error on inconsistent data")
    try:
        Character(
            name="Test",
            player="X",
            stats={"system": "dnd5e", "character_class": "Mage"},  # missing fields
        )
    except Exception as e:
        print(f"Error detected as expected:\n{e}")
