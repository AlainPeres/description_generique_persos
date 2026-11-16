# RPG Character Model

Multi-system RPG character modeling with **Pydantic v2**.

## Goals

- Describe **an RPG character** for many systems (D&D 5e, Pathfinder 1,
  Call of Cthulhu, Fate, SagaS, Daredevils, OpenQuest 3, no rules…) with **a single Python model** (a common base, `CharacterBase`, derived once per system), then
  export it to JSON and read it back.
- Make **adding a new system** simple.
- Produce a JSON Schema to check that **a character JSON matches the model**.
- **Note:** this is a character *description* tool, not a character
  *creation* tool.

## Layout

`main.py` is a thin orchestrator. `models.py` holds the common base and
knows no system; each system has its own module under `systems/`, with
everything specific to its rules:

```text
strict_model.py               StrictModel: common base class, rejects unknown fields
models.py                     CharacterBase (common base), Attribute, Skill, Ability, EquipmentItem,
                              Condition and their categories
systems/
├── common.py                 DerivedValue, fixed(...), CharacterClass, DnDAbility...
├── norules.py                SpecificValuesNoRules, NoRulesCharacter, generic_norules
├── dnd5e.py                  SpecificValuesDnD, DnDCharacter, generic_dnd5e
├── pathfinder1.py            SpecificValuesPF1, PF1Character, generic_pf1
├── cthulhu.py                SpecificValuesCthulhu, CthulhuCharacter, generic_cthulhu6
├── fate.py                   SpecificValuesFate, FateCharacter, generic_fate
├── sagas.py                  SpecificValuesSagas, SagasCharacter, generic_sagas
├── daredevils.py             SpecificValuesDaredevils, DaredevilsCharacter, generic_daredevils
└── openquest.py              SpecificValuesOpenQuest, OpenQuestCharacter, generic_openquest3
characters.py                 AnyCharacter: union of every XxxCharacter, discriminated on `system`
main.py                       imports the generic_* instances, exports JSON, validates round-trip
```

Imports go one way only: `models.py` → `systems/<game>.py` → `characters.py`
→ `main.py`. Each system module derives its own `XxxCharacter` from
`CharacterBase`, narrowing `system` to a single-value `Literal` and
`specific_values` to its own block, so there is no circular import and
type checkers know the exact block of each character class.
`characters.py` is the only file that lists every system: its `AnyCharacter`
union reads a character JSON whatever its system, and gives the JSON Schema.

Every model inherits from `StrictModel` (`extra="forbid"`): a JSON field that
the model does not know, such as a typo or an obsolete field, raises a
validation error instead of being silently dropped. The JSON Schema marks
each object with `"additionalProperties": false` accordingly.

## Architecture

A character (an `XxxCharacter`, derived from `CharacterBase`, which cannot be
created directly) starts with `system` (`"sagas"`, `"dnd5e"`…), the first field
of every JSON, then holds two complementary layers:

- **Generic layer** — system-agnostic lists usable across all RPGs
- **System-specific layer** (`specific_values`) — the block of the system, for data that can't be expressed as `name + int value`

```text
CharacterBase
├── system:           str                   (narrowed to a Literal by each XxxCharacter)
├── specific_values:  the system's block    (SpecificValuesSagas in SagasCharacter…)
├── name, description, age, occupation, background, additional_information   (free text)
├── attributes:       list[Attribute]       (name + AttributeCategory + int value)
├── skills:           list[Skill]           (name + SkillCategory + int value + optional checked,
│                                            base formula; omitted from JSON when None)
├── abilities:        list[Ability]         (name + AbilityCategory + optional int value + description + origin;
│                                            spells are category=Spell)
├── equipment:        list[EquipmentItem]   (name + ItemCategory + quantity …; money is an item
│                                            whose quantity is the amount)
├── possessions:      list[str]             (what is not carried equipment: house, land, shares …)
└── conditions:       list[Condition]       (lasting effects: name + kind Physical / Mental / Other +
                                             optional duration + description + cured)
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
single-value `Literal` with a default: the meaning of
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

Each `systems/<game>.py` module defines a `generic_<game>` `XxxCharacter` with
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
| `schema_character.json` | all systems | Pydantic JSON Schema of `AnyCharacter`: one branch per system, chosen by `system` |

## Adding a new system

1. Create `systems/xxx.py` with:
   - `SpecificValuesXxx(StrictModel)`, plus `skill_value_meaning` if the system has skills and `derived_values` if it has derived values (shared pieces come from `systems/common.py`);
   - `XxxCharacter(CharacterBase)` with `system: Literal["xxx"]` and `specific_values: SpecificValuesXxx`;
   - the `generic_xxx` template, putting numeric data in the generic `attributes` / `skills` lists
2. Add `XxxCharacter` to the `AnyCharacter` union in `characters.py`
3. Import `generic_xxx` in `main.py` and add it to the `EXPORTS` list

`models.py` never needs to change: it knows no system, which is what keeps
this scalable to dozens of systems.

Every generic `CharacterBase` field has a default (`""`, `None` or an empty list), so a
system only fills what it uses. To keep unused fields out of its JSON, pass
`exclude={...}` to `model_dump_json` in `main.py` (as `norules` does) or use
`exclude_defaults=True` to drop every field still at its default. Excluded
fields come back as their defaults when the JSON is reloaded.

## Type annotations

Python 3.10+ native syntax — no `List`, `Dict`, `Optional` or `Union` from
`typing`. Each `XxxCharacter` types `specific_values` with its own block,
so type checkers (Pylance, mypy) autocomplete the system-specific fields;
the `AnyCharacter` union is written out explicitly with `|`:

```python
class SagasCharacter(CharacterBase):
    system: Literal["sagas"]
    specific_values: SpecificValuesSagas

AnyCharacter = Annotated[
    DnDCharacter | SagasCharacter | ...,
    Field(discriminator="system"),
]
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
                   # then checks a JSON → AnyCharacter round-trip for every template
```
