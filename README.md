# RPG Character Generator

Multi-system RPG character modeling with **Pydantic v2**.

Two files coexist intentionally:

| File | Approach |
| --- | --- |
| `main.py` | System-specific model only (`specific_values` discriminated union) |
| `main1.py` | Generic model + optional system-specific block |

## Architecture (`main1.py`)

`Character` holds two complementary layers:

- **Generic layer** — system-agnostic lists usable across all RPGs
- **System-specific layer** (`specific_values`) — optional block for systems whose structure doesn't fit the generic model

```text
Character
├── name, description, occupation, background
├── attributes:       list[Attribute]       (name + int value)
├── skills:           list[Skill]           (name + SkillCategory + int value)
├── abilities:        list[Ability]         (name + AbilityCategory + int value)
├── spells:           list[Spell]           (name + SpellCategory)
├── equipment:        list[EquipmentItem]   (name + ItemCategory + quantity …)
└── specific_values:  SpecificValuesDnD | SpecificValuesCthulhu
                    | SpecificValuesFate | SpecificValuesSagas | None
```

## Generic layer — utility models

| Model | Enum | Values |
| --- | --- | --- |
| `Attribute` | — | any numeric stat (STR, DEX, HP …) |
| `Skill` | `SkillCategory` | Base / New / Specialization |
| `Ability` | `AbilityCategory` | Feat / Origin Ability / Class Ability / Power / Advantage / Disadvantage |
| `Spell` | `SpellCategory` | Base / New |
| `EquipmentItem` | `ItemCategory` | weapon / armor / item / consumable |

## System-specific layer — `specific_values` models

Used only for data that cannot be expressed as `name + int value`:

| System | Model | Specific fields |
| --- | --- | --- |
| D&D 5e | `SpecificValuesDnD` | `character_class`, `race`, `level`, `alignment`, `size`, `movement`, `languages` |
| Call of Cthulhu | `SpecificValuesCthulhu` | system marker only (data lives in generic layer) |
| FATE | `SpecificValuesFate` | `Concept`, `Aspects`, `Stunts`, `Extras`, `FatePoints` |
| SagaS | `SpecificValuesSagas` | system marker (to be completed) |

FATE is the primary use case for `specific_values`: Aspects are narrative strings (`list[str]`), incompatible with `Attribute(name, value: int)`.

## Adding a new system

1. Create `SpecificValuesXxx(BaseModel)` with `system: Literal["xxx"]`
2. Add it to the union in `Character.specific_values`
3. Put numeric data in the generic `attributes` / `skills` lists

## Type annotations

Python 3.10+ native syntax — no `List`, `Dict`, `Optional`, or `Union` from `typing`:

```python
size: str | None = None
specific_values: SpecificValuesDnD | SpecificValuesCthulhu | None = None
skills: list[Skill]
```

## Requirements

- Python >= 3.13
- pydantic >= 2.13.4

```bash
uv sync
```

## Usage

```bash
python main.py    # system-specific model
python main1.py   # generic model
```

Both output:

1. Generated JSON for each sample character (Thorin D&D, Eleanor Cthulhu)
2. Full JSON Schema
3. Exports `thorin.json`, `eleanor.json`, `schema_character.json`
4. Round-trip validation demo (`model_dump_json` → `model_validate_json`)
5. Intentional validation error demo (missing required fields)
