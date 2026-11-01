"""
Generic template for a character with no rules system.

Only narrative fields and free tags: attributes, skills and abilities are
meaningless here, so main.py leaves them out of the exported JSON.
"""

from models import Character
from systems.specific_values import SpecificValuesNoRules

generic_norules = Character(
    name="Generic no rules character",
    description="A generic character in a no rules system",
    age="to be specified",
    background="background not specified",
    additional_information="to be specified",
    specific_values=SpecificValuesNoRules(
        system="norules",
        tags=["to be specified"],
    ),
)
