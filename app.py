import os
import streamlit as st
from dotenv import load_dotenv
from src.pdf_processor import extract_pages, chunk_pages
from src.retriever import build_index, retrieve
from src.llm_handler import answer_question, summarize_document, generate_quiz

load_dotenv()
st.set_page_config(page_title="ChatPDF — GenAI Document Assistant", page_icon="📄", layout="wide")

st.title("📄 ChatPDF — GenAI Document Assistant")
st.caption("Ask questions about your PDFs. Answers are grounded in retrieved document passages.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "index" not in st.session_state:
    st.session_state.index = None
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "pages" not in st.session_state:
    st.session_state.pages = []

with st.sidebar:
    st.header("1. Upload a PDF")
    uploaded = st.file_uploader("Choose a text-based PDF", type=["pdf"])
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        st.warning("Add GROQ_API_KEY to your .env file, then restart the app.")
    st.divider()
    st.header("2. Document tools")
    num_results = st.slider("Retrieved passages per answer", 2, 8, 4)
    st.caption("Scanned/image-only PDFs need OCR first. Keep API keys private.")

if uploaded is not None:
    if st.session_state.doc_name != uploaded.name:
        try:
            raw = uploaded.getvalue()
            pages = extract_pages(raw)
            chunks = chunk_pages(pages)
            if not chunks:
                st.error("No readable text found. This may be a scanned PDF; use an OCR-enabled version.")
            else:
                with st.spinner("Creating embeddings and indexing your document…"):
                    index, embedding_model = build_index(chunks)
                st.session_state.pages = pages
                st.session_state.chunks = chunks
                st.session_state.index = index
                st.session_state.embedding_model = embedding_model
                st.session_state.doc_name = uploaded.name
                st.session_state.messages = []
                st.success(f"Loaded **{uploaded.name}** — {len(pages)} pages, {len(chunks)} text chunks.")
        except Exception as exc:
            st.error(f"Could not process this PDF: {exc}")
            st.stop()
    else:
        st.info(f"Current document: **{uploaded.name}**")
else:
    if st.session_state.doc_name:
        st.info(f"Loaded document: **{st.session_state.doc_name}**. Upload another PDF to switch documents.")
    else:
        st.info("Upload a PDF in the sidebar to begin.")

if st.session_state.index is not None:
    tab_chat, tab_tools, tab_sources = st.tabs(["💬 Chat", "✨ Summary & Quiz", "📚 Document Preview"])
    with tab_chat:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("Sources used"):
                        for source in msg["sources"]:
                            st.markdown(f"**Page {source['page']}** — {source['text']}")
        prompt = st.chat_input("Ask a question about your PDF…")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                if not groq_key:
                    st.error("GROQ_API_KEY is missing. Add it to .env and restart Streamlit.")
                else:
                    with st.spinner("Searching the PDF and generating an answer…"):
                        passages = retrieve(prompt, st.session_state.chunks,
                                            st.session_state.index,
                                            st.session_state.embedding_model,
                                            top_k=num_results)
                        history = st.session_state.messages[-7:-1]
                        result = answer_question(prompt, passages, history, groq_key)
                    st.markdown(result["answer"])
                    with st.expander("Sources used"):
                        if result["sources"]:
                            for source in result["sources"]:
                                st.markdown(f"**Page {source['page']}** — {source['text']}")
                        else:
                            st.write("No supporting passages were retrieved.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"]
                    })
    with tab_tools:
        st.subheader("Document summary")
        if st.button("Generate summary", key="summary"):
            if not groq_key:
                st.error("Add GROQ_API_KEY to .env.")
            else:
                with st.spinner("Summarizing the document in sections…"):
                    summary = summarize_document(st.session_state.chunks, groq_key)
                st.markdown(summary)
        st.divider()
        st.subheader("Generate practice quiz")
        quiz_count = st.slider("Number of questions", 3, 10, 5)
        if st.button("Generate quiz", key="quiz"):
            if not groq_key:
                st.error("Add GROQ_API_KEY to .env.")
            else:
                with st.spinner("Creating quiz from your PDF…"):
                    quiz = generate_quiz(st.session_state.chunks, quiz_count, groq_key)
                st.markdown(quiz)
    with tab_sources:
        st.subheader("Extracted text by page")
        for page in st.session_state.pages:
            with st.expander(f"Page {page['page']}"):
                st.write(page["text"] or "_No selectable text on this page._")

st.divider()
st.caption("Prototype note: answers can still be wrong. Check the cited page passages before relying on them.")
