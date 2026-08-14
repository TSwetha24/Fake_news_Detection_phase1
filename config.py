import os

# Project Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
FAKEDDIT_PATH = os.path.join(DATA_DIR, "fakeddit_sample.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
ROBERTA_MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "roberta_fakeddit")

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Module 1: Fake News Detection Settings
# Target Classes: Real, Fake, Unverified
LABELS = ["Real", "Fake", "Unverified"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for i, label in enumerate(LABELS)}

# Pretrained Transformer Models
ROBERTA_MODEL_NAME = "roberta-base"
FALLBACK_TRANSFORMER = "distilbert-base-uncased"

# Module 2: Evidence Retrieval Settings
TARGET_EVIDENCE_COUNT = 15  # Minimum 15+ articles as required
MAX_EVIDENCE_TOP_K = 25
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# Module 3: Source Independence Analysis Settings
SENTENCE_BERT_MODEL = "all-MiniLM-L6-v2"
COSINE_SIMILARITY_THRESHOLD = 0.72  # Threshold above which articles are considered syndicated/duplicates
CLUSTERING_METHOD = "agglomerative"  # Agglomerative or DBSCAN

# UI / Server Settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
DEBUG = True
