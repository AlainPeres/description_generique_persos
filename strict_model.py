"""
Common base class for every model of the project.

Lives in its own module, depending only on pydantic, so that models.py and
every systems/<game>.py module can import it without creating a circular
import.
"""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    # Reject unknown fields instead of silently dropping them, so that a
    # typo or an obsolete field in a JSON file raises a validation error.
    model_config = ConfigDict(extra="forbid")
