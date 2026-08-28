# AI Career Copilot

An isolated second project in this repository: a React + Python career assistant that retrieves resume evidence before asking Claude for a structured job-fit analysis.

## Run

From `career_copilot`:

```powershell
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Set `ANTHROPIC_API_KEY` in the repository `.env` first. The API returns a 0-100 fit score, strengths, gaps, tailoring actions, recruiter messaging, and the retrieved resume evidence used to ground the result.

## Test

```powershell
pytest career_copilot/tests -q
```
