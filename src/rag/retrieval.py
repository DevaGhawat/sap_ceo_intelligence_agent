import chromadb
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME, TOP_K
from src.pipeline.build_vector_store import COLLECTION_NAME

_embedding_model = None
_collection = None


def load_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _embedding_model


def load_collection():
    global _collection

    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        _collection = client.get_collection(name=COLLECTION_NAME)

    return _collection


def distance_to_similarity(distance: float) -> float:
    similarity = 1 / (1 + distance)
    return round(similarity, 4)


def guess_query_topic(query: str) -> str:
    query = query.lower()

    if "risk" in query or "challenge" in query or "threat" in query:
        return "risk"

    if "opportunity" in query or "prioritize" in query or "growth" in query:
        return "opportunity"

    if "competitor" in query or "competition" in query:
        return "competitor"

    if "regulation" in query or "compliance" in query or "privacy" in query:
        return "regulation"

    if "revenue" in query or "financial" in query or "earnings" in query:
        return "financial"

    if "joule" in query or "btp" in query or "ai" in query or "cloud erp" in query:
        return "technology"

    return "general"


def calculate_final_score(item, query_topic):
    similarity = item["similarity_score"]
    quality_score = float(item["quality_score"]) / 100

    topic_bonus = 0

    if item["topic"] == query_topic:
        topic_bonus = 0.08

    if query_topic == "risk" and item["topic"] in ["risk", "regulation", "financial"]:
        topic_bonus = 0.1

    final_score = similarity + (quality_score * 0.05) + topic_bonus

    return round(final_score, 4)


def retrieve_evidence(query: str, top_k: int = TOP_K, fetch_k: int = 25):
    model = load_embedding_model()
    collection = load_collection()

    query_topic = guess_query_topic(query)
    query_embedding = model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances"],
    )

    items = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for index, document_text in enumerate(documents):
        metadata = metadatas[index]
        distance = distances[index]

        item = {
            "rank": index + 1,
            "chunk_id": metadata.get("chunk_id"),
            "doc_id": metadata.get("doc_id"),
            "title": metadata.get("title"),
            "source_name": metadata.get("source_name"),
            "source_type": metadata.get("source_type"),
            "topic": metadata.get("topic"),
            "url": metadata.get("url"),
            "quality_score": metadata.get("quality_score"),
            "is_full_text": metadata.get("is_full_text"),
            "similarity_score": distance_to_similarity(distance),
            "text": document_text,
        }

        item["final_score"] = calculate_final_score(item, query_topic)
        items.append(item)

    sorted_items = sorted(
        items,
        key=lambda item: item["final_score"],
        reverse=True,
    )

    selected_items = []
    used_doc_ids = set()

    for item in sorted_items:
        doc_id = item["doc_id"]

        if doc_id in used_doc_ids:
            continue

        selected_items.append(item)
        used_doc_ids.add(doc_id)

        if len(selected_items) >= top_k:
            break

    for index, item in enumerate(selected_items, start=1):
        item["rank"] = index

    return selected_items


def format_evidence_for_prompt(evidence_items):
    blocks = []

    for item in evidence_items:
        block = f"""
Evidence ID: chunk_{item['chunk_id']}
Title: {item['title']}
Source: {item['source_name']}
Source Type: {item['source_type']}
Topic: {item['topic']}
Quality Score: {item['quality_score']}
Similarity Score: {item['similarity_score']}
Final Retrieval Score: {item['final_score']}
URL: {item['url']}

Text:
{item['text']}
"""
        blocks.append(block.strip())

    return "\n\n".join(blocks)


def show_retrieval_results(query: str, top_k: int = TOP_K):
    evidence_items = retrieve_evidence(query, top_k)

    print("\nRetrieval results")
    print(f"Query: {query}")
    print(f"Top K: {top_k}")

    for item in evidence_items:
        print("\nRank:", item["rank"])
        print("Chunk ID:", item["chunk_id"])
        print("Doc ID:", item["doc_id"])
        print("Title:", item["title"])
        print("Source:", item["source_name"])
        print("Source type:", item["source_type"])
        print("Topic:", item["topic"])
        print("Quality score:", item["quality_score"])
        print("Similarity score:", item["similarity_score"])
        print("Final score:", item["final_score"])
        print("URL:", item["url"])
        print("Text preview:")
        print(item["text"][:800])


def test_retrieval():
    queries = [
        "What are SAP's biggest risks in enterprise AI and cloud ERP?",
        "What opportunities should SAP prioritize in Business AI?",
        "How is SAP using Joule and SAP Business Technology Platform strategically?",
    ]

    for query in queries:
        show_retrieval_results(query, top_k=5)


if __name__ == "__main__":
    test_retrieval()