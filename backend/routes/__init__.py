"""API routes package for WeightAshes."""

from .ai import router as ai_router
from .codex import router as codex_router
from .manuscript import router as manuscript_router

__all__ = [
    "ai_router",
    "codex_router",
    "manuscript_router",
]
