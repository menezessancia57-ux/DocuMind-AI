import hashlib
import json
from pathlib import Path

import streamlit as st

from app.config import DATA_DIR, EMBEDDING_MODEL, GEMINI_API_KEY, GEMINI_MODEL, INDEX_PATH, METADATA_PATH, MAX_UPLOAD_MB
from app.embeddings.embedding_model import EmbeddingModel
from app.generation.generator import AnswerGenerator
from app.retrieval.semantic_retriever import SemanticRetriever
from app.retrieval.vector_store import VectorStore
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService
from app.ui.components import render_result
from app.ui.styles import load_styles

st.set_page_config(page_title="DocuMind AI", page_icon="📄", layout="wide")
load_styles()

UPLOAD_DIR = DATA_DIR / "uploads"
REGISTRY_PATH = DATA_DIR / "documind_documents.json"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

for key, default in {
    "documents": [], "query_results": [], "processing_choice": {}, "page": "Dashboard"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def load_registry():
    if not REGISTRY_PATH.exists():
        return []
    try:
        payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_registry(documents):
    REGISTRY_PATH.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")


def rebuild_seed_index():
    chunks = []
    missing_documents = []
    for document in load_registry():
        document_id = document.get("document_id")
        filename = document.get("filename")
        if not document_id or not filename:
            raise ValueError("The bundled document registry contains an invalid entry.")
        source_path = UPLOAD_DIR / f"{document_id}.pdf"
        if not source_path.is_file():
            missing_documents.append(filename)
            continue
        with source_path.open("rb") as source:
            processed = DocumentService(max_upload_mb=MAX_UPLOAD_MB).process(
                source,
                filename=filename,
            )
        if processed["document_id"] != document_id:
            raise ValueError(f"The bundled PDF does not match its registry ID: {filename}")
        chunks.extend(processed["chunks"])
    if chunks:
        retriever.index(chunks, replace=True)
    if missing_documents:
        st.warning(
            "Some bundled documents are unavailable and were not indexed: "
            + ", ".join(missing_documents)
        )


@st.cache_resource(show_spinner=False)
def get_embedding_model():
    return EmbeddingModel(EMBEDDING_MODEL)

vector_store = VectorStore(INDEX_PATH, METADATA_PATH)
embedding_model = get_embedding_model()
retriever = SemanticRetriever(embedding_model, vector_store)
generator = AnswerGenerator(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
rag_service = RAGService(retriever, generator)

if vector_store.vectors.shape[0] != len(vector_store.metadata):
    rebuild_seed_index()

if not st.session_state.documents and vector_store.metadata:
    unique = {}
    for chunk in vector_store.metadata:
        document_id = chunk.get("document_id") or chunk.get("filename", "unknown")
        unique.setdefault(document_id, {"document_id": document_id, "filename": chunk.get("filename", "Unknown"),
                                        "page_count": 0, "character_count": 0, "chunks": [], "pages": []})
        unique[document_id]["chunks"].append(chunk)
    for document in unique.values():
        document["page_count"] = len({c.get("page_number") for c in document["chunks"]})
        document["character_count"] = sum(len(c.get("text", "")) for c in document["chunks"])
    st.session_state.documents = list(unique.values())


def remove_document(document_id):
    document = next((d for d in st.session_state.documents if d["document_id"] == document_id), None)
    if not document:
        return
    vector_store.remove_document(document_id=document_id, filename=document["filename"])
    st.session_state.documents = [d for d in st.session_state.documents if d["document_id"] != document_id]
    registry = [d for d in load_registry() if d.get("document_id") != document_id]
    save_registry(registry)
    upload_path = UPLOAD_DIR / f"{document_id}.pdf"
    if upload_path.exists():
        upload_path.unlink()
    st.session_state.query_results = []


with st.sidebar:
    st.markdown("<div class='nav-brand'><span>📄</span><div><strong>DocuMind AI</strong><small>Intelligent Document Search</small></div></div>", unsafe_allow_html=True)
    st.markdown("### Navigation")
    page = st.radio("Navigation", ["Dashboard", "PDF Processing", "Semantic Search", "Ask Documents", "Settings / Diagnostics"],
                    index=["Dashboard", "PDF Processing", "Semantic Search", "Ask Documents", "Settings / Diagnostics"].index(st.session_state.page),
                    label_visibility="collapsed", key="main_navigation")
    st.session_state.page = page

if page == "Dashboard":
    st.markdown("# DocuMind AI")
    st.markdown("### Intelligent Document Search and Question Answering")
    st.write("Turn PDF evidence into searchable passages and traceable answers using document-grounded NLP and retrieval.")
    st.markdown("#### Project workflow")
    st.markdown("Upload PDF  →  Extract & preprocess  →  Create embeddings  →  Semantic Search  →  Ask questions  →  Cited answer")
    c1, c2, c3 = st.columns(3)
    cards = [
        ("PDF Processing and NLP", "PDF text extraction, cleaning, page-aware metadata, and overlapping chunks preserve document structure."),
        ("Embeddings and Semantic Search", "Sentence embeddings and vector similarity retrieve passages using meaning, including paraphrased queries."),
        ("RAG and Answer Generation", "Relevant evidence is sent to an answer model, with citations or an honest insufficient-evidence response."),
    ]
    for column, (title, body) in zip((c1, c2, c3), cards):
        with column:
            st.markdown(f"<div class='feature-card'><h3>{title}</h3><p>{body}</p></div>", unsafe_allow_html=True)
    st.markdown("#### Quick actions")
    a, b, c = st.columns(3)
    if a.button("Upload a PDF", use_container_width=True):
        st.session_state.page = "PDF Processing"; st.rerun()
    if b.button("Search documents", use_container_width=True):
        st.session_state.page = "Semantic Search"; st.rerun()
    if c.button("Ask a question", use_container_width=True):
        st.session_state.page = "Ask Documents"; st.rerun()

elif page == "PDF Processing":
    st.markdown("# PDF Processing and Library")
    uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"], accept_multiple_files=True, key="pdf_uploader")
    c1, c2 = st.columns(2)
    chunk_size = c1.number_input("Chunk size (words)", 100, 1000, 450, 50)
    overlap = c2.number_input("Chunk overlap (words)", 0, 499, 75, 25)
    if overlap >= chunk_size:
        st.warning("Chunk overlap must be smaller than chunk size.")

    if st.button("Process documents", type="primary"):
        if not uploaded_files:
            st.warning("Select one or more PDF files.")
        else:
            progress = st.progress(0, text="Preparing PDF processing")
            processed = []
            failures = []
            for index, uploaded in enumerate(uploaded_files, start=1):
                if not uploaded.name.lower().endswith(".pdf"):
                    failures.append((uploaded.name, "The file is not a PDF.")); continue
                try:
                    service = DocumentService(max_upload_mb=MAX_UPLOAD_MB, chunk_size=chunk_size, overlap=overlap)
                    result = service.process(uploaded)
                    existing_ids = {d["document_id"] for d in st.session_state.documents}
                    if result["document_id"] in existing_ids:
                        failures.append((uploaded.name, "This PDF is already in the library.")); continue
                    processed.append(result)
                except Exception as exc:
                    failures.append((uploaded.name, str(exc)))
                progress.progress(index / len(uploaded_files), text=f"Processing {uploaded.name}")
            if processed:
                new_chunks = [chunk for document in processed for chunk in document["chunks"]]
                with st.spinner("Loading embeddings and building the index…"):
                    retriever.index(new_chunks, replace=False)
                st.session_state.documents.extend(processed)
                for document in processed:
                    target = UPLOAD_DIR / f"{document['document_id']}.pdf"
                    source = next(f for f in uploaded_files if getattr(f, 'name', '') == document['filename'])
                    source.seek(0)
                    target.write_bytes(source.read())
                save_registry([{k: d[k] for k in ("document_id", "filename", "page_count", "character_count")} for d in st.session_state.documents])
                st.success(f"Processed and indexed {len(processed)} PDF(s), {len(new_chunks)} chunks.")
            progress.empty()
            for filename, error in failures:
                st.error(f"{filename}: {error}")

    for document in st.session_state.documents:
        with st.container(border=True):
            h1, h2, h3 = st.columns([4, 2, 1])
            h1.markdown(f"**{document['filename']}**")
            h2.caption(f"{document.get('page_count', 0)} pages · {len(document.get('chunks', []))} chunks")
            confirm_key = f"confirm_remove_{document['document_id']}"
            remove_key = f"remove_{document['document_id']}"
            if h3.button("Remove", key=remove_key):
                st.session_state[confirm_key] = True
            if st.session_state.get(confirm_key):
                st.warning("Remove this PDF and its indexed content?")
                yes, no = st.columns(2)
                if yes.button("Confirm removal", key=f"yes_{document['document_id']}"):
                    remove_document(document["document_id"])
                    st.session_state[confirm_key] = False
                    st.success("PDF and indexed content removed.")
                    st.rerun()
                if no.button("Cancel", key=f"no_{document['document_id']}"):
                    st.session_state[confirm_key] = False
                    st.rerun()
            with st.expander("Extracted text and chunk preview"):
                preview = "\n\n".join(page.get("text", "") for page in document.get("pages", [])[:2])
                st.text(preview[:4000] or "Indexed text is available from the vector metadata.")
                for chunk in document.get("chunks", [])[:3]:
                    st.caption(f"Page {chunk.get('page_number', '?')}")
                    st.write(chunk.get("text", "")[:1000])

elif page == "Semantic Search":
    st.markdown("# Semantic Search")
    query = st.text_input("Search your documents", placeholder="Describe the topic or use a natural-language question")
    c1, c2 = st.columns([3, 1])
    options = ["All documents"] + sorted({d["filename"] for d in st.session_state.documents})
    filename = c1.selectbox("Document filter", options)
    top_k = c2.number_input("Result count", 1, 20, 5)
    if st.button("Search", type="primary"):
        try:
            with st.spinner("Searching semantically…"):
                st.session_state.query_results = retriever.search(query, top_k=top_k, filename=filename)
        except ValueError as exc:
            st.warning(str(exc))
    if st.session_state.query_results:
        for result in st.session_state.query_results:
            render_result(result)
    elif st.session_state.documents:
        st.info("Enter a query and select Search to rank relevant passages.")
    else:
        st.info("No documents are indexed. Upload a PDF in PDF Processing first.")

elif page == "Ask Documents":
    st.markdown("# Ask Documents")
    st.caption(f"Answer mode: **{generator.mode}**")
    question = st.text_area("Question", placeholder="What does the document say about…?")
    top_k = st.slider("Evidence chunks", 1, 6, 4)
    if st.button("Ask documents", type="primary"):
        try:
            if not question.strip():
                raise ValueError("Enter a question.")
            if not vector_store.metadata:
                st.info("No documents have been indexed yet. Upload a PDF first.")
            else:
                with st.spinner("Retrieving evidence and preparing an answer…"):
                    result = rag_service.ask(question, top_k=top_k)
                answer_label = "Generated answer" if result["type"] == "generated" else "Local extractive answer"
                st.caption(answer_label)
                st.markdown(f"<div class='answer-box'>{result['answer']}</div>", unsafe_allow_html=True)
                if result.get("warning"):
                    st.warning(result["warning"])
                st.markdown("#### Supporting evidence")
                for item in result["evidence"]:
                    with st.expander(f"{item['filename']} · page {item['page_number']}"):
                        st.write(item["text"])
        except ValueError as exc:
            st.warning(str(exc))

else:
    st.markdown("# Settings / Diagnostics")
    st.markdown("## Runtime status")
    a, b = st.columns(2)
    a.metric("Answer generation", generator.mode)
    b.metric("Embedding backend", embedding_model.backend)
    c1, c2, c3 = st.columns(3)
    c1.metric("Active documents", len(st.session_state.documents))
    c2.metric("Indexed chunks", len(vector_store.metadata))
    c3.metric("Search backend", "Vector similarity")
    st.write(f"Embedding model: `{embedding_model.model_name}`")
    st.write("Gemini configured: **yes**" if generator.api_key else "Gemini configured: **no — local extractive answers are available**")
    if embedding_model.load_error:
        st.warning(f"The real embedding model could not load. Offline hash embeddings are active: {type(embedding_model.load_error).__name__}")
        st.caption("Check network access and try again. Offline results are lexical and are not Sentence Transformer results.")
    if st.button("Retry embedding model"):
        get_embedding_model.clear()
        st.cache_resource.clear()
        st.rerun()
    if st.button("Rebuild index") and st.session_state.documents:
        chunks = [chunk for document in st.session_state.documents for chunk in document.get("chunks", [])]
        if chunks:
            with st.spinner("Rebuilding index…"):
                retriever.index(chunks, replace=True)
            st.success("Index rebuilt.")
    st.markdown("## Gemini configuration")
    st.code('GEMINI_API_KEY = "your-key-here"\nGEMINI_MODEL = "gemini-2.0-flash"', language="toml")
    st.caption("Set these values in Streamlit Cloud > App settings > Secrets, or use environment variables locally. Never commit secrets.toml or API keys.")
    if st.button("Clear entire collection"):
        st.session_state.confirm_clear_all = True
    if st.session_state.get("confirm_clear_all"):
        st.warning("Clear every PDF and indexed chunk?")
        if st.button("Confirm clear all"):
            vector_store.clear()
            st.session_state.documents = []
            st.session_state.query_results = []
            save_registry([])
            st.session_state.confirm_clear_all = False
            st.success("Entire collection cleared."); st.rerun()
