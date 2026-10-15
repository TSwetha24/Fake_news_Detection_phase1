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
COSINE_SIMILARITY_THRESHOLD = 0.50  # Threshold above which articles are considered syndicated/duplicates
CLUSTERING_METHOD = "agglomerative"  # Agglomerative or DBSCAN

# UI / Server Settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
DEBUG = True

# ==============================================================================
# Bug Fix & Optimization Flags (Default: True, can be set False for rollback)
# ==============================================================================
ENABLE_KEYWORD_SEARCH_PATCH = True             # F7: Keyword extraction for search queries
ENABLE_RECENCY_RETRIEVAL_PATCH = True          # F7: when:, timespan, sortBy recency params
ENABLE_STRICT_CACHE_KEY_PATCH = True           # F5: Avoid cache key collapse on different subjects
ENABLE_CACHE_TTL_PATCH = True                  # F5: TTL for time-sensitive / breaking claims
ENABLE_DYNAMIC_UTC_DATE_PATCH = True           # F8: Dynamic UTC date instead of static 2026-08-13
ENABLE_REMOVE_CONSTANT_FALLBACKS_PATCH = True   # F6: Don't force constant defaults
ENABLE_FRESH_BM25_SEMANTIC_INDEX_PATCH = True  # F7: Index and rank freshly fetched articles
ENABLE_LOGGED_EXCEPTIONS_PATCH = True          # F6: Log errors instead of silent except: pass
ENABLE_BREAKING_NEWS_UNVERIFIED_GATE_PATCH = True # F3: Treat uncorroborated breaking news as Unverified
ENABLE_RULE_SCOPING_PATCH = True               # F1: Scope topic rules strictly to topic keywords
ENABLE_UPCOMING_EVENT_PATCH = True             # F2: Flag upcoming events as Unverified - Upcoming Event
ENABLE_DEVELOPING_STORY_PATCH = True           # F3: Flag developing stories as Unverified - Developing Story
ENABLE_GATE_SCORE_SCALING_PATCH = True         # F4: Scale score below <=24% cap to preserve module variations
ENABLE_MODULE_FAILURE_RENORM_PATCH = True      # F6: Renormalize weights when a module fails
ENABLE_TOOL_EVIDENCE_GROUNDING_PATCH = True    # F9: Module 4 tools answer only from evidence, no LLM memory
ENABLE_SOURCES_RESPONDED_UI_PATCH = True       # F10: Display x/7 sources responded in UI
CACHE_TTL_HOURS_TIME_SENSITIVE = 6.0           # TTL in hours for time-sensitive claims
CACHE_TTL_HOURS_GENERAL = 24.0                 # TTL in hours for general static claims
PIPELINE_VERSION = "2.0.0"                     # Pipeline version tag for blockchain blocks and cache validation
ENABLE_TWO_VERDICTS_ONLY = True                # Strictly binary verdicts: ONLY Real or Fake, no Unverified overrides
ENABLE_EXTENDED_ROLE_VERIFICATION_PATCH = True # General ministerial & constitutional role contradiction checking

