# DocuMind AI

DocuMind AI is a modular Streamlit NLP mini-project for PDF processing, semantic document search, and grounded question answering. It combines text extraction, chunking, Sentence Transformers embeddings, vector search, and Retrieval-Augmented Generation (RAG).

## Features

- Multi-PDF upload, validation, text extraction, and chunk previews.
- Cleaning and configurable overlapping chunks while preserving source page metadata.
- Semantic embeddings with Sentence Transformers and local FAISS-style vector ranking fallback.
- Document filtering, similarity-ranked results, and expandable evidence.
- Gemini answer generation through the current `google-genai` SDK.
- Clearly labelled local extractive answers when no API key is available.
- Source citations and insufficient-evidence handling.

## Architecture

```text
web_app.py                 Streamlit interface
app/preprocessing/         PDF extraction, cleaning, tokenization, and chunks
app/embeddings/            Sentence Transformers embedding model
app/retrieval/             Vector storage and semantic retrieval
app/generation/            Prompts, Gemini client, demo client, citations
app/services/              Document and RAG orchestration
app/ui/                    Shared styles and result components
tests/                     Automated unit tests
```

## Setup on Windows PowerShell

```powershell
cd "C:\Users\Robert S Menezes\nlp final"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If Python blocks PowerShell activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

## Run the application

```powershell
python -m streamlit run web_app.py
```

Local extractive mode requires no API key and always remains available. Optional Gemini configuration:

```powershell
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, and optionally change `GEMINI_MODEL`. Streamlit secrets and environment variables are also supported. The key is read only at runtime and is never displayed by the interface. Restart Streamlit after changing local configuration.

## Deploy on Streamlit Community Cloud

1. Push the project to a GitHub repository. Review every PDF in `data/uploads/` first; uploads are ignored by default, and only the explicitly approved sample PDF is included.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app from the repository and select `web_app.py` as the **Main file path**.
3. If Gemini answers are desired, open the app's **Settings → Secrets** and add TOML values:

   ```toml
   GEMINI_API_KEY = "your-api-key"
   GEMINI_MODEL = "gemini-2.0-flash"
   ```

   Do not add a real key to the repository, README, or `.env.example`. The app also works without Gemini and uses local extractive answers.
4. Deploy. `requirements.txt` is installed automatically. The generated vector index and metadata are excluded from Git; on first startup, the app rebuilds the index from available PDFs listed in `data/documind_documents.json`. It warns if a registered PDF is missing.

Community Cloud's local filesystem is not durable storage. Documents uploaded through the app and indexes generated at runtime may be lost after a restart or rebuild; users may need to upload documents again.

## Tests

```powershell
python -m compileall app web_app.py
python -m pytest -q
```

## Usage

1. Open **PDF Processing**, select one or more PDFs, and choose chunk settings.
2. Click **Process documents** to extract text and build the semantic index.
3. Use **Semantic Search** to rank relevant passages and filter by document.
4. Ask a grounded question in **Ask Documents** and inspect supporting evidence.

## Concepts for demonstration

- **NLP preprocessing** cleans noisy PDF text before chunking. Tokenization separates text into words; stopwords can be removed for optional analysis without changing source evidence.
- **Embeddings** map text meaning into numeric vectors, so semantically similar passages can be found even when wording differs.
- **Vector similarity search** ranks chunks by their distance in embedding space. FAISS is used conceptually for efficient vector search, with NumPy persistence included for lightweight offline operation.
- **RAG** sends only retrieved evidence to a language model with instructions to remain grounded and cite real sources.
- **Grounded answers** cite the original filename and page. An insufficient-evidence response is preferred over invented information.

## Limitations

- Image-only and scanned PDFs require OCR, which is not bundled by default.
- The first Sentence Transformers model download requires network access. An offline hash embedding fallback is available for development and demo use.
- Gemini availability depends on account configuration, network access, and API quota.
- Persistent local vectors are optimized for this educational collection rather than large-scale production search.

## Future improvements

OCR support, hybrid lexical-semantic ranking, citation highlighting, conversation history, user-specific collections, and database-backed document storage.
