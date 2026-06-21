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
- **System-specific layer** (`stats`) — optional block for systems whose structure doesn't fit the generic model (e.g. FATE Aspects, Stunts, Extras)

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

## System-specific layer — when to use `stats`

Use `stats` when a system has data structures that can't be expressed as `name + int value`:

```python
# FATE example — Aspects are narrative strings, not numbers
class StatsFATE(BaseModel):
    system: Literal["fate"]
    aspects: list[str]
    stunts: list[str]
    refresh: int
    fate_points: int
    stress: dict[str, int] = Field(default_factory=dict)
    consequences: dict[str, str] = Field(default_factory=dict)
```

Adding a new system: create the model, add it to the union in `Character.stats`. No other change needed.

## Supported systems

| System | Model | Notes |
| --- | --- | --- |
| D&D 5e | `StatsDnD` | class, race, level, alignment, ability scores, feats, skills, spells |
| Call of Cthulhu | `StatsCthulhu` | occupation, sanity, education, move, skills, spells |

## Type annotations

Python 3.10+ native syntax throughout — no `List`, `Dict`, `Optional`, or `Union` from `typing`:

```python
weight: float | None = None
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
