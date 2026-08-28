"""Resume evidence retrieval and grounded Claude generation."""

import json
import os
import re
from dataclasses import dataclass

from anthropic import Anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class Evidence:
    text: str
    score: float


def split_resume(text: str) -> list[str]:
    """Create evidence units from resume paragraphs and bullet points."""
    return [part.strip(" -\t") for part in re.split(r"\n+", text) if part.strip()]


def retrieve_evidence(resume: str, job_description: str, top_k: int = 5) -> list[Evidence]:
    units = split_resume(resume)
    if not units or not job_description.strip():
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(units + [job_description])
    scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    return [Evidence(units[index], round(float(score), 3)) for index, score in ranked[:top_k]]


PROMPT = """You are an evidence-grounded career coach. Use only the resume evidence provided.
Never invent experience, metrics, dates, employers, or skills. Return valid JSON with exactly:
fit_score (integer 0-100), summary (string), strengths (array of strings), gaps (array of strings),
tailoring (array of strings), recruiter_message (string). If evidence is insufficient, say so clearly.
Keep the recruiter message concise and professional."""


def analyze_resume(resume: str, job_description: str, evidence: list[Evidence]) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY in .env before generating recommendations.")
    context = "\n".join(f"[{i}] ({item.score}) {item.text}" for i, item in enumerate(evidence, 1))
    prompt = f"Job description:\n{job_description}\n\nRetrieved resume evidence:\n{context}"
    response = Anthropic(api_key=api_key).messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest"),
        max_tokens=1000,
        system=PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    content = "".join(block.text for block in response.content if hasattr(block, "text"))
    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError("Claude returned an invalid structured response.") from error
