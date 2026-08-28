"""FastAPI service for the Career Copilot."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .engine import analyze_resume, retrieve_evidence

app = FastAPI(title="AI Career Copilot API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


class AnalyzeRequest(BaseModel):
    resume: str = Field(min_length=20)
    job_description: str = Field(min_length=20)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    evidence = retrieve_evidence(request.resume, request.job_description)
    try:
        result = analyze_resume(request.resume, request.job_description, evidence)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"analysis": result, "evidence": [item.__dict__ for item in evidence]}
