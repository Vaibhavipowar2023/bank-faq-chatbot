import requests
import config
from vector_store import search

BASE_SYSTEM_PROMPT = (
    "You are a helpful banking assistant. Only use the provided context."
    " If unsure, say you don't know. Do NOT list sources."
)

ROLE_STYLES = {
    "customer": (
        "Explain in simple, friendly language suitable for customers."
        " Avoid legal jargon, use examples where helpful."
    ),
    "employee": (
        "Provide detailed, formal answers suitable for bank staff."
        " Include clause numbers or RBI terminology when present in context."
    ),
}

def rag_answer(query, role="customer", top_k=None):
    results = search(query, top_k=top_k)
    context = "\n\n".join([f"[{r['doc']['source']}] {r['doc']['content']}" for r in results])

    role_style = ROLE_STYLES.get(role, ROLE_STYLES["customer"])
    system_prompt = f"{BASE_SYSTEM_PROMPT} {role_style}"

    prompt = f"User question: {query}\n\nContext:\n{context}\n\nGive the best answer:"
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        resp = requests.post(f"{config.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        data = resp.json()
        if "choices" in data and data["choices"]:
            answer = data["choices"][0]["message"]["content"].strip()
        else:
            answer = "Sorry, I couldn't fetch an answer."
    except Exception:
        answer = "There was an issue contacting the language model service."

    # Strip accidental citations if any
    for marker in ["Sources:", "Source:", "References:"]:
        if marker in answer:
            answer = answer.split(marker)[0].strip()

    # Confidence from top hit (optional)
    confidence = results[0]["score"] if results else 0.0
    return answer, results, confidence
