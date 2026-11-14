# RPG Character Model

Multi-system RPG character modeling with **Pydantic v2**.

## Goals

- Describe **an RPG character** for many systems (D&D 5e, Pathfinder 1,
  Call of Cthulhu, Fate, SagaS, Daredevils, OpenQuest 3, no rules…) with **a single Python model** (`Character`), then
  export it to JSON and read it back.
- Make **adding a new system** simple.
- Produce a JSON Schema to check that **a character JSON matches the model**.
- **Note:** this is a character *description* tool, not a character
  *creation* tool.

## Layout

`main.py` is a thin orchestrator: the schema lives in `models.py`, and each
system's character data lives in its own module under `systems/`:

```text
strict_model.py               StrictModel: common base class, rejects unknown fields
attribute_category.py         AttributeCategory, shared by models.py and systems/specific_values.py
models.py                     Character, Attribute, Skill, Ability, EquipmentItem, Condition
                               imports the SpecificValues union
systems/
├── specific_values.py        SpecificValuesNoRules / DnD / PF1 / Cthulhu / Fate / SagaS / Daredevils / OpenQuest + SpecificValues union
├── norules.py                generic_norules
├── dnd5e.py                  generic_dnd5e
├── pathfinder1.py            generic_pf1
├── cthulhu.py                generic_cthulhu6
├── sagas.py                  generic_sagas
├── daredevils.py             generic_daredevils
├── openquest.py              generic_openquest3
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
├── attributes:       list[Attribute]       (name + AttributeCategory + int value)
├── skills:           list[Skill]           (name + SkillCategory + int value + optional checked,
│                                            base formula; omitted from JSON when None)
├── abilities:        list[Ability]         (name + AbilityCategory + optional int value + description + origin;
│                                            spells are category=Spell)
├── equipment:        list[EquipmentItem]   (name + ItemCategory + quantity …; money is an item
│                                            whose quantity is the amount)
├── possessions:      list[str]             (what is not carried equipment: house, land, shares …)
├── conditions:       list[Condition]       (lasting effects: name + kind Physical / Mental / Other +
│                                            optional duration + description + cured)
└── specific_values:  SpecificValues | None   (discriminated union on `system`)
```

## What is stored

**Only what cannot be computed from other values is stored.** Modifiers,
proficiency bonus, BAB, saves, Armor Class in D&D and PF1 (computed from
class, race, armor, shield, items and active spells), Idea / Luck / Know,
damage bonus, total level, Sanity / HP / MP maximums in Cthulhu, skill
levels, Protection, MaxImpactBonus, hit points, shock thresholds and Reflex
Defense in SagaS… are left out: storing them would risk inconsistencies when
the source value changes. They are computed **outside the model**, by the
tools that read the character.

Stored instead:

- *current* values (`Current Sanity`, `Current Hit Points`, SagaS wounds and
  stun…), which change during play;
- maximums that cannot be computed, such as `Maximum Hit Points` in D&D and
  PF1, rolled at each level;
- `StressBox.available` / `Consequence.available` in Fate. Fate Core gives
  a starting value from Physique or Will, but a stunt, an extra or an
  off-rules decision can change it, and no calculator can foresee every
  case: it is not derivable.

Each block lists the derived values of its system in a fixed
`derived_values` field (list of `DerivedValue`: name, `applies_to` and
sources or formula), so a reader of the JSON knows what exists and the external calculator knows
what to produce. Like `skill_value_meaning`, it has a default and any other
value is rejected (through the `fixed(...)` validator, since `Literal`
cannot hold a list). Fate and no rules have none. `applies_to` says whether
the value is single for the character (`character`, the default, e.g. maximum
HP) or whether the formula applies to each attribute of a category (`Main`, `Secondary`, `Talent` or `State`; e.g. `Main` for D&D
ability modifiers, Daredevils saving throws) or to each skill (`skill`, e.g.
Daredevils BCS, SagaS learning levels, OpenQuest expertise).

The model checks the **structure** only: types, enums, required fields,
unknown fields rejected, and the values fixed by the system
(`skill_value_meaning`, `derived_values`). It never checks the rules of the
game (a level above 20, a skill above 100, a cross-reference to a spell the
character does not know…): a GM may allow anything, and rule and formula
checks belong to the external calculator, as warnings.

The model describes a character **between two scenes**, not in mid-combat:
death saves, concentration, one-round conditions and temporary HP are not
stored. What lasts until the next rest is stored as *remaining* values
(spell slots, class resources, hit dice…), the maximums being derived.

## Generic layer — utility models

| Model | Enum | Values |
| --- | --- | --- |
| `Attribute` | `AttributeCategory` | Main (characteristics) / Secondary (other lasting stats, usually based on the main ones: SagaS Initiative, maximum HP, Move) / Talent (Daredevils Talents) / State (current values that change in play: HP, Sanity, wounds, damage) |
| `Skill` | `SkillCategory` | Base / New / Generic / Specialization |
| `Ability` | `AbilityCategory` | Feat / Origin Ability / Class Ability / Power / Advantage / Disadvantage / Spell |
| `EquipmentItem` | `ItemCategory` | weapon / armor / item / consumable / money |
| `Condition` | `ConditionKind` | Physical / Mental / Other |

`Skill.base` (optional, omitted from the JSON when `None`) is the skill's
formula over the attributes, written to be read by a human: `Agility` in
SagaS, `Deftness + Wit + Natural` in Daredevils (initial score; the first
attribute and the first talent govern), `Dexterity + 10` in OpenQuest. The
templates fill it for every listed skill; each system checks the names it
uses.

Two orthogonal axes:

- `SkillCategory` says **where** an entry comes from: `Base` = part of the
  system's official list, `New` = custom entry added by the player
  (`Generic` / `Specialization` cover open-ended skills such as *Art (…)* or
  *Pilot (…)*).
- `AbilityCategory` says **what kind** of ability it is (Feat, Power,
  Spell …).

That is why `Ability` carries both: `category: AbilityCategory` for its type
and `origin: SkillCategory` (default `Base`) for its provenance: `Base` for
an ability from the official rules, `New` for one added by the player or the
GM (house spell, custom stunt, super power outside the base rules…);
`Generic` and `Specialization` make no sense for an ability. `origin` is
descriptive only: no validator reads it. Spells are no
longer a separate model — a spell is an `Ability` with `category=Spell`, its
effect going in `description`.

## System-specific layer — `specific_values` models

Used only for data that cannot be expressed as `name + int value`.

Every block whose system has skills also declares `skill_value_meaning`, a
single-value `Literal` with a default (like `system`): the meaning of
`Skill.value` is a fixed convention per system (`proficiency level: 0 none,
1 proficient, 2 expertise` for D&D 5e, `ranks` for PF1, `percentage` for
Cthulhu, `rating on the Fate ladder` for Fate, `skill level (associated
attribute + learning level)` for SagaS, the final value played, the learning
level being derived from it, `score (0 or more);
BCS = score / 5, rounded down` for Daredevils, `percentage (0-100)` for OpenQuest 3). It is written
in each JSON so the file explains itself, and any other value is rejected.

`DnDClass` and `PF1Class` inherit from a common `CharacterClass` (name,
level); each adds its
own fields (one subclass in D&D; stackable archetypes and per-class spells in
PF1). A future class-based system can reuse it.

| System | Model | Specific fields |
| --- | --- | --- |
| No rules | `SpecificValuesNoRules` | `tags` (free-form descriptors) |
| D&D 5e | `SpecificValuesDnD` | `classes` (list of `DnDClass`: name, subclass, level; one entry per class when multiclassing; total level is their sum and is not stored), `race`, `experience_points`, `alignment`, `deity`, `size`, `speed`, `languages`, `saving_throw_proficiencies`; state between rests: `exhaustion`, `ability_reduction` (points lost per ability until a rest or a restoration; current score = score − reduction), `inspiration`, `hit_dice_remaining`, `spell_slots_remaining` (shared by all classes, keyed by spell level), `pact_slots_remaining`, `prepared_spells` (names of `Spell` abilities; empty = all known spells available), `resources_remaining` |
| Pathfinder 1 | `SpecificValuesPF1` | `classes` (list of `PF1Class`: name, archetypes, level, per-class `spells_remaining` for spontaneous casters and `prepared_spells` (`PreparedSpell`: name, level, cast) for prepared casters), `favored_class`, `race`, `experience_points`, `alignment`, `deity`, `size`, `speed`, `languages`, `additional_class_skills` (granted by traits), `ability_damage` / `ability_drain` (per ability), `negative_levels`, `hero_points` (optional rule), `resources_remaining` |
| Call of Cthulhu 6 | `SpecificValuesCthulhu` | no specific field besides `derived_values`: mental disorders are `Condition`s of kind `Mental` (duration temporary / indefinite / permanent); other data lives in generic layer, skill improvement checks use `Skill.checked` |
| FATE | `SpecificValuesFate` | `HighConcept`, `Trouble`, `Aspects`, `Extras`, `FatePoints`, `Refresh`, `PhysicalStress` / `MentalStress` (`StressBox`: available, checked), `Consequences` (`Consequence`: available, value, text; slots: Mild 2, Moderate 4, Severe 6, Extreme 8, plus the extra mild physical / mental slots) |
| SagaS | `SpecificValuesSagas` | `unspent_creation_points` (set aside for later); serious injuries are `Condition`s of kind `Physical`, or `Mental` for psychical ones; each skill's `base` is its one associated attribute (one of the 8 main or 4 secondary ones), filled in the template. Secondary attributes (Initiative, Close Combat, Ranged Combat, Speed) are always computed from the main ones plus the creation points bought for them; their final values are stored, so the JSON reads as played, and the creation bonuses are derived from them; a total must be recomputed when a main attribute changes; social class goes in `occupation`, species in `description` |
| Daredevils | `SpecificValuesDaredevils` | `attribute_loss` (points lost per attribute; current = permanent − loss), `attribute_progress` (optional rule 1.8.5b: fraction toward the next attribute point), `favored_hand`, `height`, `weight_kg`, `looks`, `freely_improvable_skills` (names of the character's skills), `critical_damage` (per hit location; it disables the body part until healed), `luck_points` (optional rule; `None` = not used), `hero_motivation`, `hero_method`, `hero_code` (role-play guides of §1.9, no game effect). Each skill's `base` is its initial-score formula, e.g. `Deftness + Wit + Natural`: it starts with the governing attribute and holds the governing talent, and is filled in the template. Finances, degrees, rank, criminal record, licenses and contacts go in `background`; Reputation is not modeled (its rules are not in the rulebook) |
| OpenQuest 3 | `SpecificValuesOpenQuest` | `concept` (one sentence), `fortune_points` (2 at start), `growth_points` (earned, not yet spent), `motives` (`Motive`: text, kind saga / quest, brought into play, completed), `religion`, `religious_rank`, `specialist_caster` (free text), `divine_spells_cast` (names of `Spell` abilities). Skill value is the total percentage; a non-human's species goes in `description`, its traits and natural weapons in `abilities`; each skill's `base` gives its base formula, e.g. `Dexterity + 10` |

## Generic templates

Each `systems/<game>.py` module defines a `generic_<game>` `Character` with
default values and the full official skill list; `main.py` exports them as
ready-to-use JSON blueprints:

| Export | System | Content |
| --- | --- | --- |
| `generic_norules.json` | No rules | narrative fields + `tags` only; `attributes`, `skills` and `abilities` are left out of the export |
| `generic_dnd5e.json` | D&D 5e | 18 base skills (value = proficiency level: 0 none, 1 proficient, 2 expertise; the total bonus is derived) + 1 example feat |
| `generic_pf1.json` | Pathfinder 1 | 35 skills (32 base + 3 generic; value = ranks, the total bonus is derived) + 1 example feat |
| `generic_cthulhu6.json` | Call of Cthulhu 6 | 60 skills (56 base + 4 generic); melee weapon skills are left out, players add them as `New` |
| `generic_sagas.json` | SagaS | 113 skills (100 base + 13 generic), at their skill level for the initial learning level (characteristics of 5, Speed 8) |
| `generic_fate.json` | FATE | 18 base skills + 1 example stunt (Feat ability) |
| `generic_openquest3.json` | OpenQuest 3 | 7 characteristics (8 each + 30 points), current HP / MP; 31 skills at their base (27 base + 4 generic), Wealth included (optional rule) |
| `generic_daredevils.json` | Daredevils | 6 attributes, 7 talents at 0, Off-hand Dexterity, Lethal / Subdual Damage; 87 skills (83 base + 4 generic) at 0, meaning not acquired (Daredevils has no base score; an acquired skill gets its initial score from the attributes and talent of the moment, then is independent of them) |
| `schema_character.json` | all systems | Pydantic JSON Schema for `Character` |

## Adding a new system

1. In `systems/specific_values.py`, create `SpecificValuesXxx(StrictModel)` with `system: Literal["xxx"]` (plus `skill_value_meaning` if the system has skills, `derived_values` if it has derived values) and add it to the `SpecificValues` union at the bottom of that file
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
