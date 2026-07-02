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
models.py                     Character, Attribute, Skill, Ability, Spell, EquipmentItem
                               builds the specific_values Union from ALL_SPECIFIC_VALUES
systems/
├── specific_values.py        SpecificValuesDnD / Cthulhu / Fate / SagaS + ALL_SPECIFIC_VALUES
├── dnd5e.py                  generic_dnd5e
├── cthulhu.py                generic_cthulhu6
└── sagas.py                  generic_sagas
main.py                       imports the generic_* instances, exports JSON, validates round-trip
```

The `SpecificValuesX` classes live in `systems/specific_values.py`, not in
`models.py` — that module only depends on pydantic, never on `Character`, so
`models.py` can import `ALL_SPECIFIC_VALUES` from it without creating a
circular import (`systems/<game>.py` modules still import `Character` from
`models.py` to build their generic character templates). `models.py` builds
`Character.specific_values`'s type as a discriminated `Union` from that list
at import time, so adding a new system never requires editing `models.py`.

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
└── specific_values:  Union[*ALL_SPECIFIC_VALUES] | None   (discriminated on `system`)
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

1. In `systems/specific_values.py`, create `SpecificValuesXxx(BaseModel)` with `system: Literal["xxx"]` and append it to `ALL_SPECIFIC_VALUES`
2. Create `systems/xxx.py`, put numeric data in the generic `attributes` / `skills` lists
3. Import the new `generic_xxx` instance in `main.py`

`models.py` never needs to change — the `specific_values` union is derived
from `ALL_SPECIFIC_VALUES` automatically, which is what keeps this scalable
to dozens of systems.

## Type annotations

Python 3.10+ native syntax — no `List`, `Dict`, or `Optional` from `typing`.
The one exception is `specific_values`, which is a discriminated union built
dynamically from `ALL_SPECIFIC_VALUES` (needs `typing.Union`, not the `|`
operator, since the member types aren't known statically):

```python
size: str | None = None
SpecificValues = Annotated[Union[tuple(ALL_SPECIFIC_VALUES)], Field(discriminator="system")]
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
