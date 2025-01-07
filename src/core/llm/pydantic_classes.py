from pydantic import BaseModel, Field


# Pydantic
from typing import List


class AliasMatch(BaseModel):
    """
    A model to represent the results of name entity resolution matching.

    This class stores potential aliases or alternate representations of a subject's name
    based on analyzing entity mentions in text. It identifies and groups different ways
    a person might be referenced (e.g., "Dr. Smith", "John Smith", "Chief Smith") while
    accounting for titles, name variations, and contextual clues to ensure matches refer
    to the same individual.

    """

    aliases: List[str] = Field(
        description="List of name variations that refer to the same individual as the subject, "
        "identified through analysis of name components and contextual evidence. "
        "Excludes similar names that refer to different individuals such as family members."
    )


class RelationshipAnalysis(BaseModel):
    """
    Represents the analyzed relationship between a subject and entity based on textual context.
    Captures the relationship category, specific relationship type, and supporting evidence.
    """

    relationship_type: str = Field(
        description="Primary category of relationship (e.g., 'Family', 'Professional', 'Educational')"
    )

    exact_relationship: str = Field(
        description="Specific directional relationship from subject to entity (e.g., 'Mother_of', 'Employee_of')"
    )

    explanation: str = Field(
        description="Evidence from context supporting the identified relationship"
    )


class RedactionResult(BaseModel):
    """Model for handling redaction results with clear separation of subject and non-subject information.

    The model ensures that only non-subject personally identifiable information (PII) is included
    in the redacted text, while preserving any mentions of the subject or their aliases.
    """

    redacted_text: List[str] = Field(
        default=[],
        description="List of specific text segments containing ONLY non-subject PII that should "
        "be redacted. Each segment should be the minimum necessary text containing the "
        "sensitive information, excluding any mentions of the subject or their aliases. "
        "Example: If text is 'John and Subject went to school', only 'John' should be "
        "in this list.",
    )

    redaction_reason: str = Field(
        default="",
        description="Concise explanation of why the text segments require redaction, "
        "specifically identifying the type of non-subject PII found (e.g., 'Contains "
        "names and details of non-subject individuals')",
    )
