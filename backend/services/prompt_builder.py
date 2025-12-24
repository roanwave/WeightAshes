"""Prompt builder service for assembling AI context."""

from pathlib import Path

from models import CodexEntryWithDescription


# Path to prompt templates
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_system_prompt() -> str:
    """Load the system prompt from the markdown file."""
    system_path = PROMPTS_DIR / "system.md"
    if system_path.exists():
        return system_path.read_text(encoding="utf-8")
    return "You are a helpful writing assistant."


def build_chat_prompt(
    message: str,
    codex_entries: list[CodexEntryWithDescription],
) -> str:
    """
    Build a chat prompt with codex context.

    Args:
        message: The user's message
        codex_entries: List of codex entries to include as context

    Returns:
        Formatted prompt string
    """
    parts = []

    # Add codex entries if any
    if codex_entries:
        parts.append("## Relevant Context\n")
        for entry in codex_entries:
            parts.append(f"### {entry.name} ({entry.type.value})")
            if entry.aliases:
                parts.append(f"*Also known as: {', '.join(entry.aliases)}*")
            parts.append("")
            parts.append(entry.description.strip())
            parts.append("")
        parts.append("---\n")

    # Add user message
    parts.append("## Your Task\n")
    parts.append(message)

    return "\n".join(parts)
