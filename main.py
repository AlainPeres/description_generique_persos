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

from pydantic import BaseModel, Field
from typing import Literal, Union, Dict, List
import json


# ---------------------------------------------------------------------------
# System-specific block: Dungeons & Dragons 5e
# ---------------------------------------------------------------------------
class StatsDnD(BaseModel):
    system: Literal["dnd5e"]
    character_class: str
    race: str
    level: int = Field(ge=1, le=20)
    strength: int = Field(ge=1, le=20)
    dexterity: int = Field(ge=1, le=20)
    constitution: int = Field(ge=1, le=20)
    intelligence: int = Field(ge=1, le=20)
    wisdom: int = Field(ge=1, le=20)
    charisma: int = Field(ge=1, le=20)
    armor_class: int
    hit_points: int
    spells: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# System-specific block: Call of Cthulhu
# ---------------------------------------------------------------------------
class StatsCthulhu(BaseModel):
    system: Literal["cthulhu"]
    occupation: str
    sanity: int = Field(ge=0, le=99)
    hit_points: int
    skills: Dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Common base
# ---------------------------------------------------------------------------
class Character(BaseModel):
    name: str
    player: str
    backstory: str = ""
    stats: Union[StatsDnD, StatsCthulhu] = Field(discriminator="system")


# ---------------------------------------------------------------------------
# Character creation
# ---------------------------------------------------------------------------
thorin = Character(
    name="Thorin Ironforge",
    player="Marie",
    backstory="Dwarf blacksmith exiled from his mountain",
    stats=StatsDnD(
        system="dnd5e",
        character_class="Fighter",
        race="Dwarf",
        level=3,
        strength=16,
        dexterity=12,
        constitution=15,
        intelligence=10,
        wisdom=11,
        charisma=8,
        armor_class=17,
        hit_points=28,
        spells=[],
    ),
)

eleanor = Character(
    name="Eleanor Whitfield",
    player="Tom",
    backstory="Librarian in Arkham",
    stats=StatsCthulhu(
        system="cthulhu",
        occupation="Librarian",
        sanity=65,
        hit_points=11,
        skills={
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
