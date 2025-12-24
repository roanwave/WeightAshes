"""Pydantic models for Codex entries."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CodexType(str, Enum):
    """Types of codex entries."""

    CHARACTER = "character"
    LOCATION = "location"
    LORE = "lore"
    OBJECT = "object"
    SUBPLOT = "subplot"
    OTHER = "other"


class Relation(BaseModel):
    """A relationship between codex entries."""

    target: str
    type: str


class CodexEntry(BaseModel):
    """Metadata for a codex entry (stored as JSON)."""

    id: str
    type: CodexType
    name: str
    aliases: list[str] = []
    tags: list[str] = []
    global_entry: bool = Field(default=False, serialization_alias="global")
    region: str | None = None
    relations: list[Relation] = []
    created: datetime
    modified: datetime

    model_config = {
        "populate_by_name": True,
    }


class CodexEntryWithDescription(CodexEntry):
    """Codex entry with its markdown description included."""

    description: str
