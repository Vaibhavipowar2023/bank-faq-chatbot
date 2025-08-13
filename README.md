
# 🏦 Bank FAQ Chatbot 
A Retrieval-Augmented Generation (RAG) powered chatbot that answers customer queries using official **RBI Circulars** and **SBI FAQs**.  
Built with **Python**, **BeautifulSoup**, **LangChain**, and a **vector database** for semantic search.

---

## 📌 Features
- **RBI PDF Circular Indexing** – Scrapes & indexes latest RBI notifications.
- **SBI FAQ Scraper** – Extracts question-answer pairs from SBI's official FAQ page.
- **Semantic Search** – Uses embeddings to find the most relevant answers.
- **Confidence Score** – Returns similarity score for each answer.
- **Multilingual Support** – Handles queries in multiple languages.
- **Dark Mode UI** (optional if UI implemented).
- **Export Chat History to PDF**.

---

## 🛠 Tech Stack
- **Python 3.10+**
- **LangChain** for RAG pipeline
- **BeautifulSoup** for web scraping
- **FAISS / ChromaDB** as vector store
- **Hugging Face / OpenAI embeddings**
- **Streamlit / Flask** for UI (optional)

---

## 📂 Project Structure
```

bank-faq-bot/
│
│── data/
│   ├── BankFAQs.csv         # Raw bank FAQ data
│   ├── processed\_faqs.csv   # Cleaned & preprocessed FAQ data
│
│── embeddings/
│   ├── faiss\_index.bin      # Saved FAISS vector index
│
│── app.py                   # Streamlit chatbot UI
│── prepare\_data.py          # Clean & preprocess raw data
│── create\_index.py          # Generate embeddings & save FAISS index
│── chatbot.py               # RAG pipeline logic
│── update\_rbi.py            # Scrapes & indexes RBI circular PDFs
│── update\_faqs.py           # Scrapes & indexes SBI FAQs
│── data\_loader.py           # Loads & chunks text
│── vector\_store.py          # Handles vector DB operations
│── config.py                # API keys, settings
│── requirements.txt         # Python dependencies
│── README.md                # Documentation

````

---

## ⚡ Installation

```bash
# 1. Clone the repository
git clone https://github.com/Vaibhavipowar2023/bank-faq-chatbot.git
cd bank-faq-chatbot

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # (Linux/Mac)
.venv\Scripts\activate      # (Windows)

# 3. Install dependencies
pip install -r requirements.txt
````

---

## 📥 Updating the Knowledge Base

### Update RBI Data

```bash
python update_rbi.py
```

### Update SBI FAQ Data

```bash
python update_faqs.py
```

This will scrape the latest data and add it to the vector database.

---

## 🚀 Running the Chatbot

If you have a Streamlit UI:

```bash
streamlit run app.py
```

If using Flask API:

```bash
python app.py
```

---

## 📊 Example Query

**User:** *"What is the process for opening an SBI savings account?"*

**Bot:** *(Provides official SBI FAQ answer with source reference and confidence score)*

---


