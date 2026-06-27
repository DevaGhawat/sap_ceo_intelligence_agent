from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_EXPORTS_DIR = DATA_DIR / "raw_exports"
PROCESSED_EXPORTS_DIR = DATA_DIR / "processed_exports"
SAMPLE_OUTPUTS_DIR = DATA_DIR / "sample_outputs"

DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "intelligence.db"

VECTOR_STORE_DIR = BASE_DIR / "vector_store"
CHROMA_DB_DIR = VECTOR_STORE_DIR / "chroma_db"

COMPANY_NAME = "SAP"

INDUSTRY = (
    "enterprise software, cloud ERP, business AI, analytics, "
    "enterprise automation, and digital transformation"
)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" #"BAAI/bge-small-en-v1.5"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 120

#for word-based chunking (not used currently)
# CHUNK_SIZE = 120
# CHUNK_OVERLAP = 25

TOP_K = 5

# OLLAMA_MODEL_NAME = "qwen3:8b"       # Better quality, slower, crash risk
# OLLAMA_MODEL_NAME = "llama3.2:3b"    # Stable backup
# OLLAMA_MODEL_NAME = "qwen2.5:3b"       # Best balance for final demo
# OLLAMA_MODEL_NAME = "llama3.1:8b"
OLLAMA_MODEL_NAME = "qwen2.5:7b"
SOURCE_TYPES = [
    "official",
    "technical",
    "financial",
    "news",
    "community",
]

TOPICS = [
    "risk",
    "opportunity",
    "competitor",
    "technology",
    "regulation",
    "financial",
    "partnership",
    "sentiment",
    "general",
]

REJECTED_TEXT_MARKERS = [
    "we use cookies",
    "accept all",
    "reject all",
    "privacy settings",
    "enable javascript",
    "subscribe to continue",
    "sign in to continue",
    "access denied",
    "403 forbidden",
    "not available in your region",
]

COMPANY_RELEVANT_TERMS = [
    "sap",
    "s/4hana",
    "s4hana",
    "sap hana",
    "sap cloud",
    "cloud erp",
    "business ai",
    "sap business ai",
    "joule",
    "rise with sap",
    "grow with sap",
    "sap btp",
    "business technology platform",
    "enterprise software",
    "enterprise ai",
    "erp",
    "supply chain management",
    "procurement",
    "successfactors",
    "ariba",
    "concur",
    "fieldglass",
    "analytics cloud",
    "oracle",
    "microsoft dynamics",
    "salesforce",
    "workday",
    "servicenow",
]


def create_project_folders():
    folders = [
        DATA_DIR,
        RAW_EXPORTS_DIR,
        PROCESSED_EXPORTS_DIR,
        SAMPLE_OUTPUTS_DIR,
        DATABASE_DIR,
        VECTOR_STORE_DIR,
        CHROMA_DB_DIR,
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)


def show_config_summary():
    print("\nProject Configuration")
    print(f"Company: {COMPANY_NAME}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Vector store: {CHROMA_DB_DIR}")
    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Chunk overlap: {CHUNK_OVERLAP}")
    print(f"Ollama model: {OLLAMA_MODEL_NAME}")


if __name__ == "__main__":
    create_project_folders()
    show_config_summary()