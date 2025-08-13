import os
import csv
from datetime import datetime
from fpdf import FPDF  # fpdf2
from googletrans import Translator
import config

translator = Translator()

LANG_NAMES_TO_CODES = {"English": "en", "Hindi": "hi", "Marathi": "mr"}

def translate_text(text, dest_lang_code):
    if dest_lang_code == "en":
        return text
    try:
        return translator.translate(text, dest=dest_lang_code).text
    except Exception:
        return text

def export_chat_to_pdf(chat_history, filename="chat_history.pdf"):
    """
    Export chat history with UTF-8 font support.
    For Devanagari (Hindi/Marathi), you should add a Unicode TTF font.
    Example uses built-in core fonts for English only. To fully support Hindi/Marathi
    install a TTF like NotoSansDevanagari and register it.
    """
    pdf = FPDF()
    pdf.add_page()

    # Use a Unicode font if you add the TTF (uncomment lines below and place TTF in project)
    # pdf.add_font("NotoSans", "", "NotoSansDevanagari-Regular.ttf", uni=True)
    # pdf.set_font("NotoSans", size=12)

    # Fallback (Latin) – works for English; for Hindi/Marathi switch to Unicode font above
    pdf.set_font("Arial", size=12)

    for q, a in chat_history:
        pdf.multi_cell(0, 8, f"User: {q}")
        pdf.ln(1)
        pdf.multi_cell(0, 8, f"Bot: {a}")
        pdf.ln(4)

    pdf.output(filename)

def ensure_logs_dir():
    os.makedirs(config.LOGS_DIR, exist_ok=True)

def log_interaction(query, answer, role, lang_code, confidence):
    ensure_logs_dir()
    is_new = not os.path.exists(config.CHAT_LOG_CSV)
    with open(config.CHAT_LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "role", "lang_code", "query", "answer", "confidence"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), role, lang_code, query, answer, f"{confidence:.4f}"])
