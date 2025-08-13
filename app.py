import os
import streamlit as st
from dotenv import load_dotenv
from data_loader import load_all_data, load_pdf_text, chunk_text
from vector_store import create_vector_store, append_documents
from chat_pipeline import rag_answer
from utils import translate_text, export_chat_to_pdf, log_interaction, LANG_NAMES_TO_CODES
import config

load_dotenv()

st.set_page_config(page_title="Bank & RBI Chatbot", layout="wide")
st.title("🏦 Bank FAQ & RBI Compliance Chatbot")

# Build index if missing
if not os.path.exists(config.VECTOR_STORE_PATH):
    with st.spinner("Building vector store from local data..."):
        docs = load_all_data()
        create_vector_store(docs)
    st.success("Vector store built successfully!")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar: Role & Upload
with st.sidebar:
    st.header("Settings")
    role = st.selectbox("User role", ["Customer", "Employee"])
    role_key = "customer" if role.lower().startswith("cust") else "employee"

    st.markdown("---")
    st.subheader("Add a Document")
    uploaded_file = st.file_uploader("Upload a PDF (ingest instantly)", type=["pdf"])
    if uploaded_file:
        with st.spinner("Reading & indexing the uploaded PDF..."):
            text = load_pdf_text(uploaded_file)
            new_chunks = chunk_text(text, source=f"Uploaded: {uploaded_file.name}")
            append_documents(new_chunks)
        st.success(f"Added {uploaded_file.name} to the knowledge base!")

# Main inputs
query = st.text_input("Ask your question:")
lang_name = st.selectbox("Language", list(LANG_NAMES_TO_CODES.keys()))
lang_code = LANG_NAMES_TO_CODES[lang_name]

if st.button("Ask"):
    if query.strip():
        # Always retrieve in English (you can translate the query if needed)
        translated_q = translate_text(query, "en")
        answer_en, results, confidence = rag_answer(translated_q, role=role_key, top_k=config.DEFAULT_TOP_K)
        final_answer = translate_text(answer_en, lang_code)

        # Save & show
        st.session_state.history.append((query, final_answer))
        st.markdown(f"**Answer:** {final_answer}")
        # st.progress(min(max(confidence, 0.0), 1.0))

        # Log for analytics
        try:
            log_interaction(query, final_answer, role_key, lang_code, confidence)
        except Exception:
            pass  # Don't crash UI if logging fails
#
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("Export Chat to PDF"):
#         export_chat_to_pdf(st.session_state.history, filename="chat_history.pdf")
#         st.success("Chat exported as PDF (chat_history.pdf)")

# with col2:
#     if st.button("Clear History"):
#         st.session_state.history = []
#         st.success("Cleared chat history")
