# RPG Character Generator

Multi-system RPG character modeling with **Pydantic v2**.

## Architecture

A shared `Character` base model holds common fields. System-specific stats are selected automatically via a **discriminated union** on the `system` field — adding a new system requires only a new model and a one-line union change.

```text
Character
├── name, description, background
├── stats: StatsDnD | StatsCthulhu  ← discriminated on "system"
│   ├── StatsDnD      (system="dnd5e")
│   └── StatsCthulhu  (system="cthulhu")
└── equipment: list[EquipmentItem]
    └── EquipmentItem
        ├── name, quantity, weight, equipped, description
        ├── category: ItemCategory  (weapon | armor | item | consumable)
        └── properties: dict[str, Any]
```

## Models

### System-specific stats

| System | Model | Key fields |
| --- | --- | --- |
| D&D 5e | `StatsDnD` | class, race, level, ability scores, armor class, hit points, feats, skills, spells |
| Call of Cthulhu | `StatsCthulhu` | occupation, sanity, hit points, skills, spells |

### Equipment

`EquipmentItem` is system-agnostic and shared across all characters. The `properties` field (`dict[str, Any]`) holds any system-specific metadata.

## Type annotations

Uses Python 3.10+ native syntax throughout — no `List`, `Dict`, `Optional`, or `Union` from `typing`:

```python
weight: float | None = None
stats: StatsDnD | StatsCthulhu
equipment: list[EquipmentItem]
```

## Requirements

- Python >= 3.13
- pydantic >= 2.13.4

```bash
uv sync
```

## Usage

```bash
python main.py
```

Outputs:

1. Generated JSON for each sample character (Thorin, Eleanor)
2. Full JSON Schema covering both systems
3. Exports `thorin.json`, `eleanor.json`, `schema_character.json`
4. Round-trip validation demo (`model_dump_json` → `model_validate_json`)
5. Intentional validation error demo (missing required fields)
