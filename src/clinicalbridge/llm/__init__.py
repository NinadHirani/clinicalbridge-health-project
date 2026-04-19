"""Groq LLM Client for AI Synthesis

Uses Groq API (llama3-70b model) for clinical text generation.
Get free API key at console.groq.com
"""

import os
from groq import AsyncGroq

GROQ_MODEL = "llama-3.1-70b-versatile"


async def synthesize(
    system_prompt: str,
    user_content: str,
    max_tokens: int = 800
) -> str:
    """
    Call Groq API for LLM synthesis. Returns response text.

    Args:
        system_prompt: System context for the LLM
        user_content: User prompt/content
        max_tokens: Max tokens in response

    Returns:
        Response text from LLM
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        # Return a mock response for testing without API key
        return "Mock response - no GROQ_API_KEY set. Set it in .env for real synthesis."

    try:
        client = AsyncGroq(api_key=api_key)
        chat = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=max_tokens,
            temperature=0.2,  # Low temp for clinical accuracy
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling Groq API: {str(e)}"
