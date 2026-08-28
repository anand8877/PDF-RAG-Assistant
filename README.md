# PDF RAG Assistant

A from-first-principles retrieval-augmented Q&A app for PDF documents. It extracts PDF text with `pypdf`, creates overlap-aware word chunks, indexes them with TF-IDF, retrieves passages with cosine similarity, and sends only those passages to Claude.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
streamlit run app.py
```

Upload PDFs, click **Index documents**, then ask a question. Claude is instructed to decline when the retrieved source does not contain the answer.

## Test

```powershell
pytest -q
```

The core retrieval code is usable independently:

```python
from rag_assistant.pipeline import DocumentStore

store = DocumentStore()
store.add_pdf("handbook.pdf")
matches = store.search("What is the vacation policy?")
```
