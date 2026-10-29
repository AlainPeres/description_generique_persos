# RPG Character Model

Multi-system RPG character modeling with **Pydantic v2**.

`main.py` is a thin orchestrator: the schema lives in `models.py`, and each
system's character data lives in its own module under `systems/`:

```text
strict_model.py               StrictModel: common base class, rejects unknown fields
models.py                     Character, Attribute, Skill, Ability, EquipmentItem
                               imports the SpecificValues union
systems/
├── specific_values.py        SpecificValuesNoRules / DnD / Cthulhu / Fate / SagaS + SpecificValues union
├── norules.py                generic_norules
├── dnd5e.py                  generic_dnd5e
├── cthulhu.py                generic_cthulhu6
├── sagas.py                  generic_sagas
└── fate.py                   generic_fate
main.py                       imports the generic_* instances, exports JSON, validates round-trip
```

The `SpecificValuesX` classes live in `systems/specific_values.py`, not in
`models.py` — that module only depends on pydantic and `strict_model.py`,
never on `Character`, so
`models.py` can import the `SpecificValues` discriminated union from it
without creating a circular import (`systems/<game>.py` modules still import
`Character` from `models.py` to build their generic character templates).
The union is written out next to the classes it lists, so adding a new
system never requires editing `models.py`.

Every model inherits from `StrictModel` (`extra="forbid"`): a JSON field that
the model does not know, such as a typo or an obsolete field, raises a
validation error instead of being silently dropped. The JSON Schema marks
each object with `"additionalProperties": false` accordingly.

## Architecture

`Character` holds two complementary layers:

- **Generic layer** — system-agnostic lists usable across all RPGs
- **System-specific layer** (`specific_values`) — optional block for data that can't be expressed as `name + int value`

```text
Character
├── name, description, age, occupation, background, additional_information   (free text)
├── attributes:       list[Attribute]       (name + int value)
├── skills:           list[Skill]           (name + SkillCategory + int value + optional checked;
│                                            checked is omitted from JSON when None)
├── abilities:        list[Ability]         (name + AbilityCategory + optional int value + description + origin;
│                                            spells are category=Spell)
├── equipment:        list[EquipmentItem]   (name + ItemCategory + quantity …)
└── specific_values:  SpecificValues | None   (discriminated union on `system`)
```

## Generic layer — utility models

| Model | Enum | Values |
| --- | --- | --- |
| `Attribute` | — | any numeric stat (STR, DEX, HP …) |
| `Skill` | `SkillCategory` | Base / New / Generic / Specialization |
| `Ability` | `AbilityCategory` | Feat / Origin Ability / Class Ability / Power / Advantage / Disadvantage / Spell |
| `EquipmentItem` | `ItemCategory` | weapon / armor / item / consumable |

Two orthogonal axes:

- `SkillCategory` says **where** an entry comes from: `Base` = part of the
  system's official list, `New` = custom entry added by the player
  (`Generic` / `Specialization` cover open-ended skills such as *Art (…)* or
  *Pilot (…)*).
- `AbilityCategory` says **what kind** of ability it is (Feat, Power,
  Spell …).

That is why `Ability` carries both: `category: AbilityCategory` for its type
and `origin: SkillCategory` (default `Base`) for its provenance. Spells are no
longer a separate model — a spell is an `Ability` with `category=Spell`, its
effect going in `description`.

## System-specific layer — `specific_values` models

Used only for data that cannot be expressed as `name + int value`:

| System | Model | Specific fields |
| --- | --- | --- |
| No rules | `SpecificValuesNoRules` | `tags` (free-form descriptors) |
| D&D 5e | `SpecificValuesDnD` | `character_class`, `race`, `level`, `experience_points`, `alignment`, `size`, `speed`, `languages` |
| Call of Cthulhu 6 | `SpecificValuesCthulhu` | `mental_disorders` (`MentalDisorder`: name, duration temporary/indefinite/permanent, description, cured); other data lives in generic layer, skill improvement checks use `Skill.checked` |
| FATE | `SpecificValuesFate` | `HighConcept`, `Trouble`, `Aspects`, `Extras`, `FatePoints`, `Refresh`, `PhysicalStress` / `MentalStress` (`StressBox`: available, checked), `Consequences` (`Consequence`: available, value, text) |
| SagaS | `SpecificValuesSagas` | `unspent_creation_points` |

## Generic templates

Each `systems/<game>.py` module defines a `generic_<game>` `Character` with
default values and the full official skill list; `main.py` exports them as
ready-to-use JSON blueprints:

| Export | System | Content |
| --- | --- | --- |
| `generic_norules.json` | No rules | narrative fields + `tags` only; `attributes`, `skills` and `abilities` are left out of the export |
| `generic_dnd5e.json` | D&D 5e | 18 base skills + 1 example feat |
| `generic_cthulhu6.json` | Call of Cthulhu 6 | 60 skills (56 base + 4 generic); melee weapon skills are left out, players add them as `New` |
| `generic_sagas.json` | SagaS | 108 skills (92 base + 16 generic) |
| `generic_fate.json` | FATE | 18 base skills + 1 example stunt (Feat ability) |
| `schema_character.json` | all systems | Pydantic JSON Schema for `Character` |

## Adding a new system

1. In `systems/specific_values.py`, create `SpecificValuesXxx(StrictModel)` with `system: Literal["xxx"]` and add it to the `SpecificValues` union at the bottom of that file
2. Create `systems/xxx.py`, put numeric data in the generic `attributes` / `skills` lists
3. Import the new `generic_xxx` instance in `main.py` and add it to the `EXPORTS` list

`models.py` never needs to change — it imports the `SpecificValues` union
as is, which is what keeps this scalable to dozens of systems.

Every `Character` field has a default (`""`, `None` or an empty list), so a
system only fills what it uses. To keep unused fields out of its JSON, pass
`exclude={...}` to `model_dump_json` in `main.py` (as `norules` does) or use
`exclude_defaults=True` to drop every field still at its default. Excluded
fields come back as their defaults when the JSON is reloaded.

## Type annotations

Python 3.10+ native syntax — no `List`, `Dict`, `Optional` or `Union` from
`typing`. The `SpecificValues` union is written out explicitly with `|`, so
type checkers (Pylance, mypy) know every member and can autocomplete
system-specific fields:

```python
size: str | None = None
SpecificValues = Annotated[
    SpecificValuesDnD | SpecificValuesCthulhu | ...,
    Field(discriminator="system"),
]
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
python main.py     # exports every generic_*.json + schema_character.json,
                   # then checks a JSON → Character round-trip for every template
```
