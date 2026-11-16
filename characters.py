"""
Registry of the rules systems: the union of every XxxCharacter class, used to
read a character JSON whatever its system, and to build the JSON Schema.

This is the only file that lists every system. To add one, create its
systems/<game>.py module and add its XxxCharacter class to the union below.
"""

from typing import Annotated

from pydantic import Field, TypeAdapter

from systems.cthulhu import CthulhuCharacter
from systems.daredevils import DaredevilsCharacter
from systems.dnd5e import DnDCharacter
from systems.fate import FateCharacter
from systems.norules import NoRulesCharacter
from systems.openquest import OpenQuestCharacter
from systems.pathfinder1 import PF1Character
from systems.sagas import SagasCharacter

# Written out explicitly so that type checkers know each member;
# `discriminator="system"` lets Pydantic pick the class from the `system`
# field instead of trying each member in turn
AnyCharacter = Annotated[
    DnDCharacter
    | PF1Character
    | CthulhuCharacter
    | FateCharacter
    | SagasCharacter
    | DaredevilsCharacter
    | OpenQuestCharacter
    | NoRulesCharacter,
    Field(discriminator="system"),
]

# Reads (validate_json) and describes (json_schema) any character
character_adapter: TypeAdapter[AnyCharacter] = TypeAdapter(AnyCharacter)
