import os
import time
import requests
from bs4 import BeautifulSoup
from data_loader import chunk_text
from vector_store import append_documents

SBI_FAQ_URL = "https://sbi.co.in/web/customer-care/faq-s"


def fetch_sbi_faqs():
    """
    Scrape FAQs from SBI's official page.
    Returns a list of (question, answer) tuples.
    """
    try:
        r = requests.get(SBI_FAQ_URL, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch SBI FAQs: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    faqs = []
    # SBI FAQ page often uses accordion or h3 + p structure
    questions = soup.select("h3, h4, .accordion-title")
    for q in questions:
        question_text = q.get_text(strip=True)
        # Get next sibling or content after the question
        answer_tag = q.find_next_sibling()
        if answer_tag:
            answer_text = answer_tag.get_text(separator=" ", strip=True)
        else:
            answer_text = ""

        if question_text and answer_text:
            faqs.append((question_text, answer_text))

    return faqs


def update_index_from_sbi():
    faqs = fetch_sbi_faqs()
    total_added = 0
    for q, a in faqs:
        try:
            chunks = chunk_text(f"Q: {q}\nA: {a}", source="SBI FAQ")
            append_documents(chunks)
            total_added += 1
            print(f"Indexed: {q[:60]}...")
        except Exception as e:
            print(f"Failed to index FAQ: {q[:30]}... | Error: {e}")

    print(f"Update complete. Total FAQs indexed: {total_added}")


if __name__ == "__main__":
    update_index_from_sbi()
