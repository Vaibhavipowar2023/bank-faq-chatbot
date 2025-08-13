import json
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def _safe_text(s: str) -> str:
    return (s or "").strip()

def load_faq_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    # Expect data to be dict of sections -> list of Q/A pairs or dicts
    for section in (data.values() if isinstance(data, dict) else [data]):
        for item in section:
            if isinstance(item, list) and len(item) == 2:
                q, a = item
            elif isinstance(item, dict):
                q = item.get("question") or item.get("q")
                a = item.get("answer") or item.get("a")
            else:
                continue
            q, a = _safe_text(q), _safe_text(a)
            if q and a:
                docs.append({"content": f"Q: {q}\nA: {a}", "source": "Bank FAQs"})
    return docs

def load_pdf_text(path_or_filelike):
    """
    Accepts a file path (str) or a bytes-like object (uploaded file).
    Returns full text.
    """
    text = ""
    if isinstance(path_or_filelike, str):
        with fitz.open(path_or_filelike) as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    # File-like (Streamlit uploader: .readable(), .getbuffer())
    file_bytes = path_or_filelike.read()
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def chunk_text(text, source, chunk_size=600, overlap=80):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return [{"content": chunk, "source": source} for chunk in splitter.split_text(text)]

def load_all_data():
    docs = []
    # FAQs
    faq_path = os.path.join("data", "bank_faqs.json")
    if os.path.exists(faq_path):
        docs.extend(load_faq_json(faq_path))

    # RBI PDFs
    pdfs = [
        ("RBI Master Circular on eKYC (2020)", os.path.join("data", "RBI_master_circular_on_eKYC_09.01.2020.pdf")),
        ("RBI Notifications - Common Person", os.path.join("data", "rbi.org.in_CommonPerson_english_scripts_NotificationPrint.html.pdf")),
    ]
    for label, path in pdfs:
        if os.path.exists(path):
            text = load_pdf_text(path)
            if text.strip():
                docs.extend(chunk_text(text, label))

    return docs
