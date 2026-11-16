"""
RPG character model (multi-system) with Pydantic.

Generates generic character templates
per system instead of named characters. Models live in models.py, and
per-system character data lives in systems/.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json

from characters import character_adapter
from models import CharacterBase
from systems.dnd5e import generic_dnd5e
from systems.pathfinder1 import generic_pf1
from systems.cthulhu import generic_cthulhu6
from systems.sagas import generic_sagas
from systems.fate import generic_fate
from systems.daredevils import generic_daredevils
from systems.openquest import generic_openquest3
from systems.norules import generic_norules


# ---------------------------------------------------------------------------
# Display: generated JSON + global JSON Schema
# ---------------------------------------------------------------------------
def print_separator(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def export_json(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  -> exported: {path}")


# Each generic template with its export path and the fields left out of its JSON
EXPORTS: list[tuple[str, CharacterBase, set[str]]] = [
    ("generic_dnd5e.json", generic_dnd5e, set()),
    ("generic_pf1.json", generic_pf1, set()),
    ("generic_cthulhu6.json", generic_cthulhu6, set()),
    ("generic_sagas.json", generic_sagas, set()),
    ("generic_fate.json", generic_fate, set()),
    ("generic_daredevils.json", generic_daredevils, set()),
    ("generic_openquest3.json", generic_openquest3, set()),
    ("generic_norules.json", generic_norules, {"attributes", "skills", "abilities"}),
]


if __name__ == "__main__":
    print_separator("JSON FILE EXPORT")
    raws: list[tuple[CharacterBase, str]] = []
    for path, character, exclude in EXPORTS:
        raw = character.model_dump_json(indent=2, exclude=exclude)
        export_json(path, raw)
        raws.append((character, raw))
    export_json("schema_character.json", json.dumps(character_adapter.json_schema(), indent=2, ensure_ascii=False))

    print_separator("VALIDATION: reload from raw JSON")
    for character, raw in raws:
        reloaded = character_adapter.validate_json(raw)
        status = "OK" if reloaded == character else "MISMATCH"
        print(f"  [{status}] {reloaded.name} ({reloaded.system})")
