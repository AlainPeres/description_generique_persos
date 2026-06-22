# RPG Character Generator

Multi-system RPG character modeling with **Pydantic v2**.

Three files with progressive scope:

| File | Role |
| --- | --- |
| `main.py` | System-specific model only (`specific_values` discriminated union) |
| `main1.py` | Generic model + optional system-specific block, named characters |
| `main2.py` | Same architecture, generates **generic character templates** per system |

## Architecture (`main1.py` / `main2.py`)

`Character` holds two complementary layers:

- **Generic layer** — system-agnostic lists usable across all RPGs
- **System-specific layer** (`specific_values`) — optional block for data that can't be expressed as `name + int value`

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
| `Skill` | `SkillCategory` | Base / New / Generic / Specialization |
| `Ability` | `AbilityCategory` | Feat / Origin Ability / Class Ability / Power / Advantage / Disadvantage |
| `Spell` | `SpellCategory` | Base / New |
| `EquipmentItem` | `ItemCategory` | weapon / armor / item / consumable |

## System-specific layer — `specific_values` models

Used only for data that cannot be expressed as `name + int value`:

| System | Model | Specific fields |
| --- | --- | --- |
| D&D 5e | `SpecificValuesDnD` | `character_class`, `race`, `level`, `alignment`, `size`, `speed`, `languages`, `reflex_save`, `fortitude_save`, `will_save` |
| Call of Cthulhu 6 | `SpecificValuesCthulhu` | system marker only (data lives in generic layer) |
| FATE | `SpecificValuesFate` | `Concept`, `Aspects`, `Stunts`, `Extras`, `FatePoints` |
| SagaS | `SpecificValuesSagas` | system marker (to be completed) |

## Generic templates (`main2.py`)

`main2.py` generates ready-to-use JSON blueprints with default values and the full official skill list for each system:

| Export | System | Skills |
| --- | --- | --- |
| `generic_dnd5e.json` | D&D 5e | 18 base skills |
| `generic_cthulhu6.json` | Call of Cthulhu 6 | ~55 skills (base + generic) |
| `generic_sagas.json` | SagaS | ~90 skills across all categories |

## Adding a new system

1. Create `SpecificValuesXxx(BaseModel)` with `system: Literal["xxx"]`
2. Add it to the union in `Character.specific_values`
3. Put numeric data in the generic `attributes` / `skills` lists
4. Optionally add a generic template instance in `main2.py`

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
python main.py     # system-specific model, named characters
python main1.py    # generic model, named characters
python main2.py    # generic model, system templates → JSON exports
```
