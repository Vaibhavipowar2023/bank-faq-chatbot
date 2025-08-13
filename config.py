import os
from dotenv import load_dotenv
load_dotenv()

# API keys (OpenRouter / DeepSeek)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Models
LLM_MODEL = "deepseek/deepseek-r1:free"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # HuggingFace model

# Paths
EMBEDDINGS_DIR = "embeddings"
VECTOR_STORE_PATH = os.path.join(EMBEDDINGS_DIR, "vector_store.pkl")
METADATA_PATH = os.path.join(EMBEDDINGS_DIR, "metadata.pkl")

DATA_DIR = "data"
LOGS_DIR = "logs"
CHAT_LOG_CSV = os.path.join(LOGS_DIR, "chat_logs.csv")

# App
DEFAULT_TOP_K = 5
