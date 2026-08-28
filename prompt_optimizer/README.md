# Prompt Optimizer

An AI prompt engineering workbench that rewrites loose requests with Claude meta-prompting, then compares baseline and engineered outputs side by side.

## Run

```powershell
cd prompt_optimizer
npm install
Copy-Item .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
npm start
```

Open `http://localhost:3000`. The workbench supports role framing, task decomposition, output-format specification, constraints, expected outcomes, zero-shot rewriting, and optional few-shot examples. Its transparent local score measures instruction coverage before the Claude comparison runs.

## Test

```powershell
npm test
```
