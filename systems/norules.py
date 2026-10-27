from models import Character
from systems.specific_values import SpecificValuesNoRules

generic_norules = Character(
    name="Generic no rules character",
    description="A generic character in a no rules system",
    background="background not specified",
    specific_values=SpecificValuesNoRules(
        system="norules",       
        tags=["to be specified"],
    ),  
)

