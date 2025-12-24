"""Pydantic models for Manuscript structure."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SceneStatus(str, Enum):
    """Status of a scene in the writing process."""

    DRAFT = "draft"
    REVISED = "revised"
    FINAL = "final"


class Scene(BaseModel):
    """Metadata for a scene (stored as JSON)."""

    id: str
    title: str
    summary: str = ""
    pov: str | None = None
    word_count: int = Field(default=0, serialization_alias="wordCount")
    status: SceneStatus = SceneStatus.DRAFT
    labels: list[str] = []
    attached_codex: list[str] = Field(
        default=[], serialization_alias="attachedCodex"
    )
    created: datetime
    modified: datetime

    model_config = {
        "populate_by_name": True,
    }


class SceneWithContent(Scene):
    """Scene with its markdown content included."""

    content: str


class Chapter(BaseModel):
    """Metadata for a chapter (stored as meta.json)."""

    id: str
    title: str
    summary: str = ""
    scenes: list[str] = []
    word_count: int = Field(default=0, serialization_alias="wordCount")
    status: SceneStatus = SceneStatus.DRAFT

    model_config = {
        "populate_by_name": True,
    }


class Act(BaseModel):
    """Metadata for an act."""

    id: str
    title: str
    chapters: list[str] = []


class Book(BaseModel):
    """Metadata for a book."""

    id: str
    title: str
    acts: list[str] = []
