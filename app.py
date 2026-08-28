"""Streamlit interface for the PDF RAG Assistant."""

from pathlib import Path
import tempfile

import streamlit as st

from rag_assistant.answering import answer_question
from rag_assistant.pipeline import DocumentStore


st.set_page_config(page_title="PDF RAG Assistant", page_icon="PDF", layout="wide")
st.title("PDF RAG Assistant")
st.caption("Ask questions grounded in the documents you upload.")

if "store" not in st.session_state:
    st.session_state.store = DocumentStore()

uploaded_files = st.file_uploader("Upload PDF documents", type="pdf", accept_multiple_files=True)
if uploaded_files and st.button("Index documents", type="primary"):
    store = DocumentStore()
    with tempfile.TemporaryDirectory() as temp_dir:
        paths = []
        for uploaded_file in uploaded_files:
            path = Path(temp_dir) / uploaded_file.name
            path.write_bytes(uploaded_file.getvalue())
            paths.append(path)
        chunk_count = store.add_pdfs(paths)
    st.session_state.store = store
    st.success(f"Indexed {chunk_count} passages from {len(uploaded_files)} document(s).")

question = st.text_input("Question", placeholder="What does the document say about...")
if st.button("Ask", disabled=not question or not st.session_state.store.chunks):
    with st.spinner("Searching documents and asking Claude..."):
        matches = st.session_state.store.search(question)
        try:
            st.session_state.answer = answer_question(question, matches)
            st.session_state.matches = matches
        except RuntimeError as error:
            st.error(str(error))

if "answer" in st.session_state:
    st.subheader("Answer")
    st.write(st.session_state.answer)
    with st.expander("Retrieved passages"):
        for index, chunk in enumerate(st.session_state.matches, start=1):
            st.markdown(f"**[{index}] {chunk.source}, page {chunk.page or '?'}**  ")
            st.caption(f"Similarity: {chunk.score:.3f}")
            st.write(chunk.text)
