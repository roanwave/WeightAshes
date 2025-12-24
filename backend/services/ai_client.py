"""AI client service for interacting with LLM providers."""

import os
from typing import TypedDict

import anthropic


class GenerateResult(TypedDict):
    """Result from generate function."""

    response: str
    input_tokens: int
    output_tokens: int


async def generate(
    prompt: str,
    system: str,
    model: str = "claude-sonnet-4-20250514",
) -> GenerateResult:
    """
    Generate a response from the AI model.

    Args:
        prompt: The user message/prompt
        system: The system message
        model: The model to use (default: claude-sonnet-4-20250514)

    Returns:
        Dict with response text and token counts
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return {
            "response": "Error: ANTHROPIC_API_KEY not configured. Please add it to your .env file.",
            "input_tokens": 0,
            "output_tokens": 0,
        }

    try:
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        # Extract text from response
        response_text = ""
        for block in message.content:
            if hasattr(block, "text"):
                response_text += block.text

        return {
            "response": response_text,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }

    except anthropic.APIConnectionError:
        return {
            "response": "Error: Could not connect to Anthropic API. Please check your internet connection.",
            "input_tokens": 0,
            "output_tokens": 0,
        }
    except anthropic.RateLimitError:
        return {
            "response": "Error: Rate limit exceeded. Please wait a moment and try again.",
            "input_tokens": 0,
            "output_tokens": 0,
        }
    except anthropic.APIStatusError as e:
        return {
            "response": f"Error: API error ({e.status_code}): {e.message}",
            "input_tokens": 0,
            "output_tokens": 0,
        }
    except Exception as e:
        return {
            "response": f"Error: Unexpected error: {str(e)}",
            "input_tokens": 0,
            "output_tokens": 0,
        }
