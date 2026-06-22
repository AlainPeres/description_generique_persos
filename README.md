# RPG Character Generator

Multi-system RPG character modeling with **Pydantic v2**.

Two files coexist intentionally:

| File | Approach |
| --- | --- |
| `main.py` | System-specific model only (`stats` discriminated union) |
| `main1.py` | Generic model + optional system-specific block |

## Architecture (`main1.py`)

`Character` holds two complementary layers:

- **Generic layer** — system-agnostic lists usable across all RPGs
- **System-specific layer** (`stats`) — optional block for systems whose structure doesn't fit the generic model

```text
Character
├── name, description, occupation, background
├── attributes:  list[Attribute]          (name + int value)
├── skills:      list[Skill]              (name + SkillCategory + int value)
├── abilities:   list[Ability]            (name + AbilityCategory + int value)
├── spells:      list[Spell]              (name + SpellCategory)
├── equipment:   list[EquipmentItem]      (name + ItemCategory + quantity …)
└── stats:       StatsDnD | StatsCthulhu | None   ← optional, system-specific
```

## Generic layer — utility models

| Model | Enum | Values |
| --- | --- | --- |
| `Attribute` | — | any numeric stat (STR, DEX, HP …) |
| `Skill` | `SkillCategory` | Base / New / Specialization |
| `Ability` | `AbilityCategory` | Feat / Origin Ability / Class Ability / Power / Advantage / Disadvantage |
| `Spell` | `SpellCategory` | Base / New |
| `EquipmentItem` | `ItemCategory` | weapon / armor / item / consumable |

## System-specific layer — `stats` models

`stats` is used only for data that cannot be expressed as `name + int value`:

| System | Model | Champs système-spécifiques |
| --- | --- | --- |
| D&D 5e | `StatsDnD` | `character_class`, `race`, `level`, `alignment`, `size`, `movement` |
| Call of Cthulhu | `StatsCthulhu` | marqueur système uniquement (données dans la couche générique) |
| FATE | `StatsFate` | `Concept`, `Aspects`, `Stunts`, `Extras`, `FatePoints` |
| SagaS | `StatsSagas` | marqueur système (à compléter) |

FATE illustre le cas d'usage principal de `stats` : les Aspects sont des phrases narratives (`list[str]`), incompatibles avec `Attribute(name, value: int)`.

## Ajouter un nouveau système

1. Créer le modèle `StatsXxx(BaseModel)` avec `system: Literal["xxx"]`
2. L'ajouter à l'union dans `Character.stats`
3. Instancier les données communes dans la couche générique (`attributes`, `skills`…)

## Type annotations

Python 3.10+ native syntax — no `List`, `Dict`, `Optional`, or `Union` from `typing`:

```python
size: str | None = None
stats: StatsDnD | StatsCthulhu | None = None
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
