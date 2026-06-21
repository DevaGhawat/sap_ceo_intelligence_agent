import shutil

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME
from src.database import fetch_all_chunks


COLLECTION_NAME = "sap_strategic_chunks"


def reset_vector_store():
    if CHROMA_DB_DIR.exists():
        shutil.rmtree(CHROMA_DB_DIR)

    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)


def load_embedding_model():
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return model


def create_metadata(chunk):
    metadata = {
        "chunk_id": str(chunk["chunk_id"]),
        "doc_id": str(chunk["doc_id"]),
        "chunk_index": str(chunk["chunk_index"]),
        "title": chunk["title"] or "",
        "url": chunk["url"] or "",
        "source_name": chunk["source_name"] or "",
        "source_type": chunk["source_type"] or "",
        "topic": chunk["topic"] or "",
        "published_date": chunk["published_date"] or "",
        "quality_score": int(chunk["quality_score"] or 0),
        "is_full_text": int(chunk["is_full_text"] or 0),
    }

    return metadata


def build_vector_store():
    reset_vector_store()

    chunks = fetch_all_chunks()

    print("\nBuilding vector store")
    print(f"Chunks available: {len(chunks)}")
    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")

    if not chunks:
        print("No chunks found. Run chunking first.")
        return

    model = load_embedding_model()

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    batch_size = 64
    total_added = 0

    for start_index in range(0, len(chunks), batch_size):
        batch = chunks[start_index:start_index + batch_size]

        texts = [chunk["chunk_text"] for chunk in batch]
        ids = [str(chunk["chunk_id"]) for chunk in batch]
        metadatas = [create_metadata(chunk) for chunk in batch]

        embeddings = model.encode(texts, show_progress_bar=False)
        embeddings = embeddings.tolist()

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        total_added += len(batch)
        print(f"Embedded chunks: {total_added}/{len(chunks)}")

    print("\nVector store summary")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Chunks embedded: {total_added}")
    print(f"Vector store path: {CHROMA_DB_DIR}")


if __name__ == "__main__":
    build_vector_store()