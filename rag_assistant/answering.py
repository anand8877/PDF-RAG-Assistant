"""Claude answer generation with explicit source-grounding instructions."""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

from .pipeline import RetrievedChunk

load_dotenv()


SYSTEM_PROMPT = """You answer questions only from the supplied document excerpts.
If the excerpts do not contain enough information to answer, say exactly:
I couldn't find that in the uploaded documents.
Do not use outside knowledge. Cite supporting excerpts as [1], [2], etc. Keep the answer concise."""


def answer_question(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "I couldn't find that in the uploaded documents."
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY in .env before asking a question.")
    context = "\n\n".join(
        f"[{index}] {chunk.source}, page {chunk.page or '?'}\n{chunk.text}"
        for index, chunk in enumerate(chunks, start=1)
    )
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest"),
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Document excerpts:\n{context}\n\nQuestion: {question}"}],
    )
    return "".join(block.text for block in response.content if hasattr(block, "text"))
