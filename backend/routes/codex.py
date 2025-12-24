"""API routes for Codex CRUD operations."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from models import CodexEntry, CodexEntryWithDescription, CodexType
from services import (
    delete_codex_entry,
    get_codex_entry,
    list_codex_entries,
    save_codex_entry,
)

router = APIRouter(prefix="/api/codex", tags=["codex"])


class CodexCreateRequest(BaseModel):
    """Request body for creating a codex entry."""

    id: str | None = None
    type: CodexType
    name: str
    aliases: list[str] = []
    tags: list[str] = []
    global_entry: bool = False
    region: str | None = None
    relations: list[dict] = []
    description: str = ""


class CodexUpdateRequest(BaseModel):
    """Request body for updating a codex entry."""

    type: CodexType | None = None
    name: str | None = None
    aliases: list[str] | None = None
    tags: list[str] | None = None
    global_entry: bool | None = None
    region: str | None = None
    relations: list[dict] | None = None
    description: str | None = None


@router.get("/search")
async def search_codex(
    q: str = Query(..., min_length=1, description="Search query")
) -> list[CodexEntry]:
    """
    Search codex entries by name, aliases, tags, and description.
    Simple case-insensitive substring search.
    """
    all_entries = await list_codex_entries()
    query_lower = q.lower()
    results = []

    for entry in all_entries:
        # Check name
        if query_lower in entry.name.lower():
            results.append(entry)
            continue

        # Check aliases
        if any(query_lower in alias.lower() for alias in entry.aliases):
            results.append(entry)
            continue

        # Check tags
        if any(query_lower in tag.lower() for tag in entry.tags):
            results.append(entry)
            continue

        # Check description (need to load full entry)
        full_entry = await get_codex_entry(entry.id)
        if full_entry and query_lower in full_entry.description.lower():
            results.append(entry)

    return results


@router.get("/")
async def list_entries(
    type: CodexType | None = Query(None, description="Filter by entry type")
) -> list[CodexEntry]:
    """List all codex entries, optionally filtered by type."""
    type_str = type.value if type else None
    return await list_codex_entries(type_str)


@router.get("/{entry_id}")
async def get_entry(entry_id: str) -> CodexEntryWithDescription:
    """Get a single codex entry by ID, including description."""
    entry = await get_codex_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry '{entry_id}' not found")
    return entry


@router.post("/")
async def create_entry(request: CodexCreateRequest) -> CodexEntryWithDescription:
    """Create a new codex entry."""
    now = datetime.now(timezone.utc)

    # Generate ID if not provided
    entry_id = request.id or str(uuid.uuid4())[:8]

    # Check if entry already exists
    existing = await get_codex_entry(entry_id)
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Entry '{entry_id}' already exists"
        )

    # Create the entry
    entry = CodexEntry(
        id=entry_id,
        type=request.type,
        name=request.name,
        aliases=request.aliases,
        tags=request.tags,
        global_entry=request.global_entry,
        region=request.region,
        relations=request.relations,
        created=now,
        modified=now,
    )

    await save_codex_entry(entry, request.description)

    # Return the saved entry with description
    return CodexEntryWithDescription(
        **entry.model_dump(),
        description=request.description,
    )


@router.put("/{entry_id}")
async def update_entry(
    entry_id: str, request: CodexUpdateRequest
) -> CodexEntryWithDescription:
    """Update an existing codex entry."""
    # Load existing entry
    existing = await get_codex_entry(entry_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Entry '{entry_id}' not found")

    # Merge updates
    update_data = request.model_dump(exclude_unset=True)
    description = update_data.pop("description", None)
    if description is None:
        description = existing.description

    # Build updated entry
    entry_data = existing.model_dump()
    entry_data.update(update_data)
    entry_data["modified"] = datetime.now(timezone.utc)

    # Remove description from entry_data (it's stored separately)
    entry_data.pop("description", None)

    entry = CodexEntry.model_validate(entry_data)
    await save_codex_entry(entry, description)

    # Return updated entry with description
    return CodexEntryWithDescription(
        **entry.model_dump(),
        description=description,
    )


@router.delete("/{entry_id}")
async def delete_entry(entry_id: str) -> dict:
    """Delete a codex entry."""
    deleted = await delete_codex_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Entry '{entry_id}' not found")
    return {"deleted": True}
