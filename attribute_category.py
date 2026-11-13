"""
AttributeCategory: nature of a numeric stat.

Kept in its own module, like StrictModel, because both models.py (Attribute)
and systems/specific_values.py (DerivedValue.applies_to) use it, and
specific_values.py cannot import models.py without a circular import.
"""

from enum import Enum


# Nature of a numeric stat, fixed by the rules
class AttributeCategory(str, Enum):
    MAIN = "Main"                     # characteristics: Strength, DEX, Wit...
    SECONDARY = "Secondary"           # other lasting stats, usually based on the main
                                      # ones: SagaS Initiative, maximum HP, Move...
    TALENT = "Talent"                 # aptitudes: Daredevils Talents
    STATE = "State"                   # current values that change in play: HP,
                                      # Sanity, wounds, damage...
