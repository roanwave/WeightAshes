"""File manager service for codex and manuscript I/O."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import aiofiles

from models import (
    Chapter,
    CodexEntry,
    CodexEntryWithDescription,
    Scene,
    SceneWithContent,
)

# Directory configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CODEX_DIR = DATA_DIR / "codex"
MANUSCRIPT_DIR = DATA_DIR / "manuscript"
SESSIONS_DIR = DATA_DIR / "sessions"


def count_words(text: str) -> int:
    """Count words in text, excluding markdown syntax."""
    # Remove markdown headers
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    # Remove markdown emphasis
    text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
    # Remove markdown links
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    # Split and count non-empty words
    words = text.split()
    return len(words)


async def find_file_by_id(
    base_dir: Path, file_id: str, extension: str
) -> Path | None:
    """Recursively search for a file by ID."""
    if not base_dir.exists():
        return None

    pattern = f"{file_id}{extension}"
    for path in base_dir.rglob(pattern):
        if path.is_file():
            return path
    return None


# ============================================================================
# Codex Functions
# ============================================================================


async def list_codex_entries(entry_type: str | None = None) -> list[CodexEntry]:
    """
    List all codex entries, optionally filtered by type.
    Recursively scan CODEX_DIR for .json files.
    Return list of CodexEntry (metadata only, no description).
    """
    entries = []

    if not CODEX_DIR.exists():
        return entries

    # If filtering by type, only scan that subdirectory
    if entry_type:
        search_dirs = [CODEX_DIR / entry_type]
    else:
        search_dirs = [CODEX_DIR]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for json_path in search_dir.rglob("*.json"):
            try:
                async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
                    data = json.loads(await f.read())
                    # Handle 'global' -> 'global_entry' mapping
                    if "global" in data:
                        data["global_entry"] = data.pop("global")
                    entry = CodexEntry.model_validate(data)
                    entries.append(entry)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue

    return entries


async def get_codex_entry(entry_id: str) -> CodexEntryWithDescription | None:
    """
    Find a codex entry by ID across all type directories.
    Load both the .json metadata and .md description.
    Return CodexEntryWithDescription or None if not found.
    """
    json_path = await find_file_by_id(CODEX_DIR, entry_id, ".json")
    if not json_path:
        return None

    # Load JSON metadata
    try:
        async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
            data = json.loads(await f.read())
            # Handle 'global' -> 'global_entry' mapping
            if "global" in data:
                data["global_entry"] = data.pop("global")
    except (json.JSONDecodeError, FileNotFoundError):
        return None

    # Load markdown description
    md_path = json_path.with_suffix(".md")
    description = ""
    if md_path.exists():
        try:
            async with aiofiles.open(md_path, "r", encoding="utf-8") as f:
                description = await f.read()
        except FileNotFoundError:
            pass

    data["description"] = description
    return CodexEntryWithDescription.model_validate(data)


async def save_codex_entry(entry: CodexEntry, description: str) -> None:
    """
    Save a codex entry.
    Determine directory based on entry.type and entry.region (if applicable).
    Write .json metadata and .md description.
    Update the 'modified' timestamp.
    """
    # Determine directory path
    type_dir = CODEX_DIR / entry.type.value

    # For characters and locations, use region subdirectory if specified
    if entry.type.value in ("characters", "character", "locations", "location"):
        if entry.region:
            type_dir = type_dir / entry.region

    # Ensure directory exists
    type_dir.mkdir(parents=True, exist_ok=True)

    # Update modified timestamp
    entry.modified = datetime.now(timezone.utc)

    # Serialize to JSON with alias mapping
    data = entry.model_dump(by_alias=True, mode="json")

    # Write JSON file
    json_path = type_dir / f"{entry.id}.json"
    async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    # Write markdown file
    md_path = type_dir / f"{entry.id}.md"
    async with aiofiles.open(md_path, "w", encoding="utf-8") as f:
        await f.write(description)


async def delete_codex_entry(entry_id: str) -> bool:
    """
    Delete a codex entry by ID.
    Remove both .json and .md files.
    Return True if deleted, False if not found.
    """
    json_path = await find_file_by_id(CODEX_DIR, entry_id, ".json")
    if not json_path:
        return False

    # Remove JSON file
    json_path.unlink(missing_ok=True)

    # Remove markdown file
    md_path = json_path.with_suffix(".md")
    md_path.unlink(missing_ok=True)

    return True


# ============================================================================
# Manuscript Functions
# ============================================================================


async def get_manuscript_structure() -> dict:
    """
    Return the full manuscript tree structure.
    Scan MANUSCRIPT_DIR for books, acts, chapters.
    Return nested dict with structure.
    """
    result = {"books": []}

    if not MANUSCRIPT_DIR.exists():
        return result

    # Scan for books (top-level directories)
    for book_dir in sorted(MANUSCRIPT_DIR.iterdir()):
        if not book_dir.is_dir():
            continue

        book = {
            "id": book_dir.name,
            "title": book_dir.name.replace("-", " ").title(),
            "acts": [],
        }

        # Scan for acts
        for act_dir in sorted(book_dir.iterdir()):
            if not act_dir.is_dir():
                continue

            act = {
                "id": act_dir.name,
                "title": act_dir.name.replace("-", " ").title(),
                "chapters": [],
            }

            # Scan for chapters
            for chapter_dir in sorted(act_dir.iterdir()):
                if not chapter_dir.is_dir():
                    continue

                # Load chapter metadata
                meta_path = chapter_dir / "meta.json"
                if meta_path.exists():
                    try:
                        async with aiofiles.open(
                            meta_path, "r", encoding="utf-8"
                        ) as f:
                            chapter_data = json.loads(await f.read())
                    except (json.JSONDecodeError, FileNotFoundError):
                        chapter_data = {
                            "id": chapter_dir.name,
                            "title": chapter_dir.name.replace("-", " ").title(),
                        }
                else:
                    chapter_data = {
                        "id": chapter_dir.name,
                        "title": chapter_dir.name.replace("-", " ").title(),
                    }

                chapter = {
                    "id": chapter_data.get("id", chapter_dir.name),
                    "title": chapter_data.get("title", chapter_dir.name),
                    "scenes": [],
                }

                # Scan for scenes (JSON files that aren't meta.json)
                for scene_file in sorted(chapter_dir.glob("*.json")):
                    if scene_file.name == "meta.json":
                        continue

                    try:
                        async with aiofiles.open(
                            scene_file, "r", encoding="utf-8"
                        ) as f:
                            scene_data = json.loads(await f.read())
                            chapter["scenes"].append(
                                {
                                    "id": scene_data.get(
                                        "id", scene_file.stem
                                    ),
                                    "title": scene_data.get(
                                        "title", scene_file.stem
                                    ),
                                }
                            )
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue

                act["chapters"].append(chapter)

            book["acts"].append(act)

        result["books"].append(book)

    return result


async def get_scene(
    book_id: str, act_id: str, chapter_id: str, scene_id: str
) -> SceneWithContent | None:
    """
    Load a specific scene by its path components.
    Load both .json metadata and .md content.
    Return SceneWithContent or None if not found.
    """
    chapter_dir = MANUSCRIPT_DIR / book_id / act_id / chapter_id
    json_path = chapter_dir / f"{scene_id}.json"
    md_path = chapter_dir / f"{scene_id}.md"

    if not json_path.exists():
        return None

    # Load JSON metadata
    try:
        async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
            data = json.loads(await f.read())
            # Handle camelCase -> snake_case mapping
            if "wordCount" in data:
                data["word_count"] = data.pop("wordCount")
            if "attachedCodex" in data:
                data["attached_codex"] = data.pop("attachedCodex")
    except (json.JSONDecodeError, FileNotFoundError):
        return None

    # Load markdown content
    content = ""
    if md_path.exists():
        try:
            async with aiofiles.open(md_path, "r", encoding="utf-8") as f:
                content = await f.read()
        except FileNotFoundError:
            pass

    data["content"] = content
    return SceneWithContent.model_validate(data)


async def save_scene(
    book_id: str, act_id: str, chapter_id: str, scene: Scene, content: str
) -> None:
    """
    Save a scene.
    Write .json metadata and .md content.
    Update 'modified' timestamp and calculate word_count from content.
    """
    chapter_dir = MANUSCRIPT_DIR / book_id / act_id / chapter_id
    chapter_dir.mkdir(parents=True, exist_ok=True)

    # Update timestamp and word count
    scene.modified = datetime.now(timezone.utc)
    scene.word_count = count_words(content)

    # Serialize to JSON with alias mapping
    data = scene.model_dump(by_alias=True, mode="json")

    # Write JSON file
    json_path = chapter_dir / f"{scene.id}.json"
    async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    # Write markdown file
    md_path = chapter_dir / f"{scene.id}.md"
    async with aiofiles.open(md_path, "w", encoding="utf-8") as f:
        await f.write(content)


async def get_chapter(
    book_id: str, act_id: str, chapter_id: str
) -> Chapter | None:
    """Load chapter metadata from meta.json."""
    meta_path = MANUSCRIPT_DIR / book_id / act_id / chapter_id / "meta.json"

    if not meta_path.exists():
        return None

    try:
        async with aiofiles.open(meta_path, "r", encoding="utf-8") as f:
            data = json.loads(await f.read())
            # Handle camelCase -> snake_case mapping
            if "wordCount" in data:
                data["word_count"] = data.pop("wordCount")
    except (json.JSONDecodeError, FileNotFoundError):
        return None

    return Chapter.model_validate(data)


async def save_chapter(book_id: str, act_id: str, chapter: Chapter) -> None:
    """Save chapter metadata to meta.json."""
    chapter_dir = MANUSCRIPT_DIR / book_id / act_id / chapter.id
    chapter_dir.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with alias mapping
    data = chapter.model_dump(by_alias=True, mode="json")

    # Write meta.json
    meta_path = chapter_dir / "meta.json"
    async with aiofiles.open(meta_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))
