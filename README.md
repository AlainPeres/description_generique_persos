# RPG Character Generator

Multi-system RPG character modeling with **Pydantic v2**.

Three entry-point files with progressive scope:

| File | Role |
| --- | --- |
| `main0.py` | System-specific model only (`specific_values` discriminated union) |
| `main1.py` | Generic model + optional system-specific block, named characters |
| `main.py` | Same architecture, generates **generic character templates** per system |

`main.py` is a thin orchestrator: the schema lives in `models.py`, and each
system's character data lives in its own module under `systems/`:

```text
models.py            Character, Attribute, Skill, Ability, Spell, EquipmentItem,
                      SpecificValuesDnD / Cthulhu / Fate / SagaS
systems/
├── dnd5e.py          generic_dnd5e
├── cthulhu.py        generic_cthulhu6
└── sagas.py          generic_sagas
main.py               imports the generic_* instances, exports JSON, validates round-trip
```

The `SpecificValuesX` classes stay in `models.py` rather than in `systems/`,
since `Character.specific_values` needs to see all of them to build its
union type — putting them in `systems/` would create a circular import
(`systems/*.py` already imports `Character` from `models.py`). Only the bulky
per-system attribute/skill data is split out.

## Architecture (`main1.py` / `main.py`)

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

## Generic templates (`main.py`)

`main.py` generates ready-to-use JSON blueprints with default values and the full official skill list for each system:

| Export | System | Skills |
| --- | --- | --- |
| `generic_dnd5e.json` | D&D 5e | 18 base skills |
| `generic_cthulhu6.json` | Call of Cthulhu 6 | ~55 skills (base + generic) |
| `generic_sagas.json` | SagaS | ~90 skills across all categories |
| `schema_character.json` | all systems | Pydantic JSON Schema for `Character` |

## Adding a new system

1. Create `SpecificValuesXxx(BaseModel)` with `system: Literal["xxx"]` in `models.py`
2. Add it to the union in `Character.specific_values`
3. Create `systems/xxx.py`, put numeric data in the generic `attributes` / `skills` lists
4. Import the new `generic_xxx` instance in `main.py`

## Type annotations

Python 3.10+ native syntax — no `List`, `Dict`, `Optional`, or `Union` from `typing`:

```python
size: str | None = None
specific_values: SpecificValuesDnD | SpecificValuesCthulhu | SpecificValuesFate | SpecificValuesSagas | None = None
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
python main0.py    # system-specific model, named characters
python main1.py    # generic model, named characters
python main.py     # generic model, system templates → JSON exports
```
