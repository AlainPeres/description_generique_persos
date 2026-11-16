"""
No rules: system-specific block (free tags), the NoRulesCharacter class, and the
generic template for a character with no rules system.

Only narrative fields and free tags: attributes, skills and abilities are
meaningless here, so main.py leaves them out of the exported JSON.
"""

from pydantic import Field
from typing import Literal

from models import CharacterBase
from strict_model import StrictModel


# ---------------------------------------------------------------------------
# System-specific block: No Rules
# ---------------------------------------------------------------------------
class SpecificValuesNoRules(StrictModel):
    tags: list[str] = Field(default_factory=list)   # free descriptors: "brave", "noble"...


class NoRulesCharacter(CharacterBase):
    system: Literal["norules"]
    specific_values: SpecificValuesNoRules


# ---------------------------------------------------------------------------
# Generic template
# ---------------------------------------------------------------------------
generic_norules = NoRulesCharacter(
    system="norules",
    name="Generic no rules character",
    description="A generic character in a no rules system",
    age="to be specified",
    background="background not specified",
    additional_information="to be specified",
    specific_values=SpecificValuesNoRules(
        tags=["to be specified"],
    ),
)
