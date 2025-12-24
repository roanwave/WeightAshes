"""API routes for Manuscript operations."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models import Chapter, Scene, SceneStatus, SceneWithContent
from services import (
    get_chapter,
    get_manuscript_structure,
    get_scene,
    save_chapter,
    save_scene,
    count_words,
    MANUSCRIPT_DIR,
)

router = APIRouter(prefix="/api/manuscript", tags=["manuscript"])


class ChapterUpdateRequest(BaseModel):
    """Request body for updating a chapter."""

    title: str | None = None
    summary: str | None = None
    status: SceneStatus | None = None


class SceneCreateRequest(BaseModel):
    """Request body for creating a scene."""

    id: str | None = None
    title: str
    summary: str = ""
    pov: str | None = None
    status: SceneStatus = SceneStatus.DRAFT
    labels: list[str] = []
    attached_codex: list[str] = []
    content: str = ""


class SceneUpdateRequest(BaseModel):
    """Request body for updating a scene."""

    title: str | None = None
    summary: str | None = None
    pov: str | None = None
    status: SceneStatus | None = None
    labels: list[str] | None = None
    attached_codex: list[str] | None = None
    content: str | None = None


@router.get("/")
async def get_structure() -> dict:
    """Return full manuscript tree structure."""
    return await get_manuscript_structure()


@router.get("/{book_id}/{act_id}/{chapter_id}")
async def get_chapter_metadata(
    book_id: str, act_id: str, chapter_id: str
) -> Chapter:
    """Get chapter metadata."""
    chapter = await get_chapter(book_id, act_id, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter '{chapter_id}' not found",
        )
    return chapter


@router.put("/{book_id}/{act_id}/{chapter_id}")
async def update_chapter(
    book_id: str, act_id: str, chapter_id: str, request: ChapterUpdateRequest
) -> Chapter:
    """Update chapter metadata."""
    chapter = await get_chapter(book_id, act_id, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter '{chapter_id}' not found",
        )

    # Merge updates
    update_data = request.model_dump(exclude_unset=True)
    chapter_data = chapter.model_dump()
    chapter_data.update(update_data)

    updated_chapter = Chapter.model_validate(chapter_data)
    await save_chapter(book_id, act_id, updated_chapter)

    return updated_chapter


@router.get("/{book_id}/{act_id}/{chapter_id}/{scene_id}")
async def get_scene_content(
    book_id: str, act_id: str, chapter_id: str, scene_id: str
) -> SceneWithContent:
    """Get scene with content."""
    scene = await get_scene(book_id, act_id, chapter_id, scene_id)
    if not scene:
        raise HTTPException(
            status_code=404,
            detail=f"Scene '{scene_id}' not found",
        )
    return scene


@router.post("/{book_id}/{act_id}/{chapter_id}/scenes")
async def create_scene(
    book_id: str, act_id: str, chapter_id: str, request: SceneCreateRequest
) -> SceneWithContent:
    """Create a new scene."""
    # Check chapter exists
    chapter = await get_chapter(book_id, act_id, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter '{chapter_id}' not found",
        )

    now = datetime.now(timezone.utc)
    scene_id = request.id or f"scene-{str(uuid.uuid4())[:8]}"

    # Check if scene already exists
    existing = await get_scene(book_id, act_id, chapter_id, scene_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Scene '{scene_id}' already exists",
        )

    # Create scene
    scene = Scene(
        id=scene_id,
        title=request.title,
        summary=request.summary,
        pov=request.pov,
        word_count=count_words(request.content),
        status=request.status,
        labels=request.labels,
        attached_codex=request.attached_codex,
        created=now,
        modified=now,
    )

    await save_scene(book_id, act_id, chapter_id, scene, request.content)

    # Update chapter's scenes list
    if scene_id not in chapter.scenes:
        chapter.scenes.append(scene_id)
        await save_chapter(book_id, act_id, chapter)

    return SceneWithContent(**scene.model_dump(), content=request.content)


@router.put("/{book_id}/{act_id}/{chapter_id}/{scene_id}")
async def update_scene(
    book_id: str,
    act_id: str,
    chapter_id: str,
    scene_id: str,
    request: SceneUpdateRequest,
) -> SceneWithContent:
    """Update a scene."""
    existing = await get_scene(book_id, act_id, chapter_id, scene_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Scene '{scene_id}' not found",
        )

    # Merge updates
    update_data = request.model_dump(exclude_unset=True)
    content = update_data.pop("content", None)
    if content is None:
        content = existing.content

    scene_data = existing.model_dump()
    scene_data.pop("content", None)  # Remove content from scene data
    scene_data.update(update_data)
    scene_data["modified"] = datetime.now(timezone.utc)
    scene_data["word_count"] = count_words(content)

    scene = Scene.model_validate(scene_data)
    await save_scene(book_id, act_id, chapter_id, scene, content)

    return SceneWithContent(**scene.model_dump(), content=content)


@router.delete("/{book_id}/{act_id}/{chapter_id}/{scene_id}")
async def delete_scene(
    book_id: str, act_id: str, chapter_id: str, scene_id: str
) -> dict:
    """Delete a scene."""
    # Check scene exists
    existing = await get_scene(book_id, act_id, chapter_id, scene_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Scene '{scene_id}' not found",
        )

    # Delete scene files
    chapter_dir = MANUSCRIPT_DIR / book_id / act_id / chapter_id
    json_path = chapter_dir / f"{scene_id}.json"
    md_path = chapter_dir / f"{scene_id}.md"

    json_path.unlink(missing_ok=True)
    md_path.unlink(missing_ok=True)

    # Update chapter's scenes list
    chapter = await get_chapter(book_id, act_id, chapter_id)
    if chapter and scene_id in chapter.scenes:
        chapter.scenes.remove(scene_id)
        await save_chapter(book_id, act_id, chapter)

    return {"deleted": True}
