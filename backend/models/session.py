"""Pydantic models for Session and AI request logging."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AIProvider(str, Enum):
    """Supported AI providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


class AIRequestLog(BaseModel):
    """Log entry for an AI request/response."""

    id: str
    timestamp: datetime
    provider: AIProvider
    model: str
    prompt_template: str
    context_entries: list[str] = []
    token_count_input: int
    token_count_output: int
    full_prompt: str
    response: str
    scene_id: str | None = None
    duration_ms: int
