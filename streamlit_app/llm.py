from __future__ import annotations

from openai import OpenAI

from vector_db.config import load_settings
from dotenv import load_dotenv
load_dotenv()

def generate_answer(
    question: str,
    context_text: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    settings = load_settings()
    if not settings.groq_api_key:
        return context_text

    client = OpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a data assistant. Answer only from the provided context. "
                "If multiple context snippets are provided, synthesize across them. "
                "If context is insufficient, say what is missing."
            ),
        },
    ]
    if history:
        messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": f"Question: {question}\n\nContext:\n{context_text}",
        }
    )
    response = client.chat.completions.create(
        model=settings.chat_model,
        temperature=0.1,
        messages=messages,
    )
    return response.choices[0].message.content or context_text
