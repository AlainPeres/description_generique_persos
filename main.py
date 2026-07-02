"""
RPG character generation (multi-system) with Pydantic.

Same architecture as main1.py, but generates generic character templates
per system instead of named characters. Models live in models.py, and
per-system character data lives in systems/.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json

from models import Character
from systems.dnd5e import generic_dnd5e
from systems.cthulhu import generic_cthulhu6
from systems.sagas import generic_sagas
from systems.fate import generic_fate


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
    print_separator("JSON FILE EXPORT")
    export_json("generic_dnd5e.json", generic_dnd5e.model_dump_json(indent=2))
    export_json("generic_cthulhu6.json", generic_cthulhu6.model_dump_json(indent=2))
    export_json("generic_sagas.json", generic_sagas.model_dump_json(indent=2))
    export_json("generic_fate.json", generic_fate.model_dump_json(indent=2))    
    export_json("schema_character.json", json.dumps(Character.model_json_schema(), indent=2, ensure_ascii=False))

    print_separator("VALIDATION: reload from raw JSON")
    raw = generic_dnd5e.model_dump_json()
    reloaded = Character.model_validate_json(raw)
    system = reloaded.specific_values.system if reloaded.specific_values else "no system"
    print(f"Reloaded character: {reloaded.name} ({system})")
