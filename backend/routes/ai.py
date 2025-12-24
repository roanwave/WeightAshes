"""API routes for AI chat operations."""

from fastapi import APIRouter
from pydantic import BaseModel

from services import get_codex_entry
from services.ai_client import generate
from services.prompt_builder import build_chat_prompt, load_system_prompt

router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatRequest(BaseModel):
    """Request body for AI chat."""

    message: str
    context_entries: list[str] = []
    scene_id: str | None = None


class TokenUsage(BaseModel):
    """Token usage information."""

    input: int
    output: int


class ChatResponse(BaseModel):
    """Response from AI chat."""

    response: str
    tokens_used: TokenUsage


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI with optional codex context.

    Args:
        request: Chat request with message and optional context

    Returns:
        AI response with token usage
    """
    # Load codex entries for context
    codex_entries = []
    for entry_id in request.context_entries:
        entry = await get_codex_entry(entry_id)
        if entry:
            codex_entries.append(entry)

    # Build the prompt
    prompt = build_chat_prompt(request.message, codex_entries)

    # Load system prompt
    system = load_system_prompt()

    # Generate response
    result = await generate(prompt=prompt, system=system)

    return ChatResponse(
        response=result["response"],
        tokens_used=TokenUsage(
            input=result["input_tokens"],
            output=result["output_tokens"],
        ),
    )
