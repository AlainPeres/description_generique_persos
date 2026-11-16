"""
Fate Core: system-specific block and derived values, the FateCharacter
class, and the generic character template.

Default values ("to be specified", skills at +0) are meant to be replaced
when describing an actual character. Fate has no numeric attributes: the
character is described by aspects, skills, stunts, stress and consequences.
"""

from pydantic import Field
from typing import Literal

from models import CharacterBase, Attribute, Skill, SkillCategory, Ability, AbilityCategory
from strict_model import StrictModel


# ---------------------------------------------------------------------------
# System-specific block: Fate
# ---------------------------------------------------------------------------
# `available` (StressBox and Consequence) starts from Physique / Will in Fate
# Core, but stunts, extras or off-rules decisions can change it in ways no
# calculator can foresee: it is not derivable, so it is stored
class StressBox(StrictModel):
    available: bool = True    # the box exists for this character
    checked: bool = False     # the box is ticked

class Consequence(StrictModel):
    available: bool = True    # the slot exists for this character
    value: int                # stress absorbed: 2, 4, 6 or 8 depending on severity
    text: str = ""            # the consequence suffered, e.g. "Broken arm"

class SpecificValuesFate(StrictModel):
    skill_value_meaning: Literal["rating on the Fate ladder"] = "rating on the Fate ladder"
    HighConcept: str          # main aspect: who the character is
    Trouble: str              # aspect that gets the character into trouble
    Aspects: list[str] = Field(default_factory=list)  # the other aspects
    Extras: list[str] = Field(default_factory=list)   # gear, allies, powers given as aspects
    FatePoints: int           # current points
    Refresh: int              # points restored at the start of a session
    # Stress tracks, keyed by box name ("Box 1" to "Box 4")
    PhysicalStress: dict[str, StressBox] = Field(default_factory=dict)
    MentalStress: dict[str, StressBox] = Field(default_factory=dict)
    # Keyed by slot name ("Mild", "Moderate", "Severe", "Extreme", "Mild Physical"...)
    Consequences: dict[str, Consequence] = Field(default_factory=dict)


class FateCharacter(CharacterBase):
    system: Literal["fate"]
    specific_values: SpecificValuesFate


# ---------------------------------------------------------------------------
# Generic template
# ---------------------------------------------------------------------------
generic_fate = FateCharacter(
    system="fate",
    name="Generic Fate Core Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesFate(
        HighConcept="to be specified",
        Trouble="to be specified",
        Aspects=["to be specified"],
        Extras=["to be specified"],
        FatePoints=0,
        Refresh=3,                # Fate Core default, with 3 free stunts
        # Every character has 2 boxes per track; boxes 3 and 4 are unlocked
        # by Physique (physical) or Will (mental), hence available=False here.
        # `available` is stored, not derived: stunts, extras or off-rules
        # decisions can change it in ways no calculator can foresee.
        PhysicalStress={"Box 1": StressBox(), "Box 2": StressBox(),
                        "Box 3": StressBox(available=False),
                        "Box 4": StressBox(available=False)},
        MentalStress={"Box 1": StressBox(), "Box 2": StressBox(),
                      "Box 3": StressBox(available=False),
                      "Box 4": StressBox(available=False)},
        # Mild, Moderate and Severe absorb 2, 4 and 6 stress. The extra mild
        # slots are unlocked by a Superb (+5) Physique or Will. Extreme
        # absorbs 8 and permanently replaces one of the character's aspects;
        # it can be used once between two major milestones.
        Consequences={"Mild": Consequence(value=2),
                      "Moderate": Consequence(value=4),
                      "Severe": Consequence(value=6),
                      "Extreme": Consequence(value=8),
                      "Mild Physical": Consequence(value=2, available=False),
                      "Mild Mental": Consequence(value=2, available=False)},
    ),    
    skills=[
        Skill(name="Athletics", category=SkillCategory.BASE, value=0),
        Skill(name="Burglary", category=SkillCategory.BASE, value=0),
        Skill(name="Contacts", category=SkillCategory.BASE, value=0),
        Skill(name="Crafts", category=SkillCategory.BASE, value=0),
        Skill(name="Deceive", category=SkillCategory.BASE, value=0),
        Skill(name="Drive", category=SkillCategory.BASE, value=0),
        Skill(name="Empathy", category=SkillCategory.BASE, value=0),
        Skill(name="Fight", category=SkillCategory.BASE, value=0),
        Skill(name="Investigate", category=SkillCategory.BASE, value=0),
        Skill(name="Lore", category=SkillCategory.BASE, value=0),
        Skill(name="Notice", category=SkillCategory.BASE, value=0),
        Skill(name="Physique", category=SkillCategory.BASE, value=0),
        Skill(name="Provoke", category=SkillCategory.BASE, value=0),
        Skill(name="Rapport", category=SkillCategory.BASE, value=0),
        Skill(name="Resources", category=SkillCategory.BASE, value=0),
        Skill(name="Shoot",   category=SkillCategory.BASE, value=0),
        Skill(name="Stealth", category=SkillCategory.BASE, value=0),
        Skill(name="Will", category=SkillCategory.BASE, value=0),       
    ],
    # Stunts are Feat abilities, flagged as such in their description
    abilities=[
        Ability(name="to be specified", category=AbilityCategory.FEAT,
                description="Stunt"),
    ],
)
