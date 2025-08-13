import os
import re
import time
import requests
from bs4 import BeautifulSoup
from data_loader import load_pdf_text, chunk_text
from vector_store import append_documents
import config

BASE_URL = "https://rbi.org.in"
NOTIF_URL = "https://rbi.org.in/Scripts/NotificationUser.aspx"

def fetch_new_pdfs(limit=5):
    """
    Scrapes the RBI notifications page for new PDF links.
    Basic example: adjust selectors if RBI changes HTML.
    """
    try:
        r = requests.get(NOTIF_URL, timeout=30)
        r.raise_for_status()
    except Exception:
        print("Failed to fetch RBI notifications.")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a")
    pdf_urls = []
    for a in links:
        href = a.get("href", "")
        if href.lower().endswith(".pdf"):
            full = href if href.startswith("http") else f"{BASE_URL}/{href.lstrip('/')}"
            pdf_urls.append((a.text.strip() or "RBI Circular", full))

    # naive de-dup + limit
    seen = set()
    out = []
    for title, url in pdf_urls:
        if url not in seen:
            seen.add(url)
            out.append((title, url))
        if len(out) >= limit:
            break
    return out

def download_pdf(url, save_dir="data"):
    os.makedirs(save_dir, exist_ok=True)
    filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", url.split("/")[-1]) or f"rbi_{int(time.time())}.pdf"
    path = os.path.join(save_dir, filename)
    if os.path.exists(path):
        return path, False
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        return path, True
    except Exception:
        return None, False

def update_index_from_rbi():
    found = fetch_new_pdfs(limit=10)
    total_added = 0
    for title, url in found:
        path, is_new = download_pdf(url)
        if not path:
            continue
        if not is_new:
            continue  # already present
        try:
            text = load_pdf_text(path)
            chunks = chunk_text(text, source=f"RBI: {title}")
            append_documents(chunks)
            total_added += 1
            print(f"Indexed: {title}")
        except Exception:
            print(f"Failed to index: {title}")

    print(f"Update complete. New PDFs indexed: {total_added}")

if __name__ == "__main__":
    update_index_from_rbi()
