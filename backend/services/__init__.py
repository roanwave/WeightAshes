"""Services package for WeightAshes."""

from .file_manager import (
    # Configuration
    DATA_DIR,
    CODEX_DIR,
    MANUSCRIPT_DIR,
    SESSIONS_DIR,
    # Helpers
    count_words,
    find_file_by_id,
    # Codex functions
    list_codex_entries,
    get_codex_entry,
    save_codex_entry,
    delete_codex_entry,
    # Manuscript functions
    get_manuscript_structure,
    get_scene,
    save_scene,
    get_chapter,
    save_chapter,
)

from .ai_client import generate as ai_generate
from .prompt_builder import build_chat_prompt, load_system_prompt

__all__ = [
    # Configuration
    "DATA_DIR",
    "CODEX_DIR",
    "MANUSCRIPT_DIR",
    "SESSIONS_DIR",
    # Helpers
    "count_words",
    "find_file_by_id",
    # Codex
    "list_codex_entries",
    "get_codex_entry",
    "save_codex_entry",
    "delete_codex_entry",
    # Manuscript
    "get_manuscript_structure",
    "get_scene",
    "save_scene",
    "get_chapter",
    "save_chapter",
    # AI
    "ai_generate",
    "build_chat_prompt",
    "load_system_prompt",
]
