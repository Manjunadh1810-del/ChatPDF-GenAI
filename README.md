# ChatPDF — Generative AI PDF Assistant

A Streamlit mini project that lets users upload a text-based PDF, ask questions, retrieve relevant passages using semantic search, and generate answers with Groq. Includes document summaries, practice quizzes, and page-level source excerpts.

## Features
- Upload a PDF and extract selectable text page by page.
- Chunk text with overlap and preserve page numbers.
- Embed chunks using `sentence-transformers/all-MiniLM-L6-v2`.
- Retrieve relevant chunks with FAISS cosine similarity (normalized embeddings + inner product).
- Generate document-grounded answers using Groq chat completions.
- Display retrieved source excerpts and page numbers.
- Generate a document summary and MCQ quiz.
- Keep API keys in `.env`, never in source code.

## Requirements
- Python 3.10–3.12 recommended.
- Internet access for first-time Python package/model downloads and Groq API calls.
- A Groq API key from the official Groq Console.
- Text-based PDFs. Scanned PDFs require OCR before upload.

## Setup (Windows PowerShell)
```powershell
cd ChatPDF-GenAI
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```
Paste your API key after `GROQ_API_KEY=` and save the file. Do not share or commit `.env`.

If PowerShell blocks activation, use:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Setup (macOS/Linux)
```bash
cd ChatPDF-GenAI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
streamlit run app.py
```

## Run
```bash
streamlit run app.py
```
Streamlit prints a local URL, normally `http://localhost:8501`.

## How to test
1. Upload a text-based PDF (a class note or a small public-domain document).
2. Ask: `What are the main topics covered in this document?`
3. Ask a question whose answer is explicitly present in the PDF; check that the response matches the text and lists source pages.
4. Ask a question that is not covered; the assistant should say it could not find the answer in the PDF.
5. Click **Generate summary** and review whether it stays grounded in the document.
6. Click **Generate quiz** and check each correct answer against the source.
7. Upload another PDF and verify that the previous chat is reset for the new document.

## Architecture
PDF upload → PyMuPDF extraction → overlapping text chunks → Sentence Transformers embeddings → FAISS retrieval → Groq LLM → answer + source excerpts.

## Important limitations
- Scanned/image-only PDFs have no selectable text; OCR is not included.
- The first embedding-model download may take time and disk space.
- Very large PDFs may use significant RAM. Summary and quiz generation intentionally limit the number of chunks sent to the model.
- The app shows retrieved source excerpts, but an LLM can still make mistakes. Verify important claims.
- Groq model availability and rate limits can change. If the default model is unavailable for your account, set `GROQ_MODEL` in `.env` to a currently supported chat model and restart the app.
- The first time you run the app, the embedding model may download from Hugging Face.

## Security
- Never commit `.env` or share API keys in screenshots.
- Uploaded PDF content is sent to Groq only as excerpts used for answering, summary, and quiz requests. Review the provider's data and privacy terms before uploading confidential documents.
- This demo has no authentication or multi-user isolation. Do not deploy publicly without adding access control, upload limits, and privacy protections.

## Troubleshooting
- `GROQ_API_KEY is missing`: check that `.env` is in the project root and restart Streamlit.
- Model not found / unavailable: set `GROQ_MODEL` to a model listed for your account in Groq Console.
- `No readable text found`: the PDF may be scanned; OCR it first or use a text-based PDF.
- Installation fails on a new Python version: use Python 3.11 or 3.12 in a fresh virtual environment.
- FAISS or PyTorch installation errors: upgrade pip and use a supported 64-bit Python version.

## Suggested GitHub description
A retrieval-augmented generation (RAG) application built with Streamlit, Groq, Sentence Transformers, and FAISS that answers questions from PDF documents with page-level source excerpts.
