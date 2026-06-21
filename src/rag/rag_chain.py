from langchain_ollama import OllamaLLM

from src.config import OLLAMA_MODEL_NAME, TOP_K
from src.rag.retrieval import retrieve_evidence
from src.rag.prompts import build_ceo_prompt


def load_llm():
    llm = OllamaLLM(
        model=OLLAMA_MODEL_NAME,
        temperature=0.0,
        num_ctx=3072,
        num_predict=900,
        num_gpu=0,
    )

    return llm

def retrieve_strategic_evidence(question: str):
    search_plan = [
        {
            "category": "Main CEO question",
            "query": question,
            "top_k": 3,
        },
        {
            "category": "Opportunity evidence",
            "query": (
                "What opportunities should SAP prioritize in Business AI, "
                "Joule, SAP BTP, cloud ERP, and autonomous enterprise?"
            ),
            "top_k": 3,
        },
        {
            "category": "Risk evidence",
            "query": (
                "What risks or challenges does SAP face in enterprise AI, "
                "cloud ERP, fragmented data, AI governance, auditability, "
                "and implementation complexity?"
            ),
            "top_k": 3,
        },
        {
            "category": "External market evidence",
            "query": (
                "external industry news enterprise AI risks cloud ERP risks "
                "AI governance technology debt process gaps CIO enterprise software "
                "TechTarget CIO Dive SAP ERP AI market pressure"
            ),
            "top_k": 3,
        },
        {
            "category": "Customer adoption evidence",
            "query": (
                "How are customers adopting SAP Cloud ERP, GROW with SAP, "
                "RISE with SAP, and SAP Business AI?"
            ),
            "top_k": 3,
        },
    ]

    combined_items = []
    used_doc_ids = set()

    for search_item in search_plan:
        search_top_k = search_item["top_k"]

        if search_item["category"] == "External market evidence":
            search_top_k = 10

        evidence_items = retrieve_evidence(
            search_item["query"],
            top_k=search_top_k,
        )

        if search_item["category"] == "External market evidence":
            evidence_items = [
                item for item in evidence_items
                if item["source_type"] == "external_news"
            ][:3]

        for item in evidence_items:
            doc_id = item["doc_id"]

            if doc_id in used_doc_ids:
                continue

            item["evidence_category"] = search_item["category"]
            combined_items.append(item)
            used_doc_ids.add(doc_id)

    return combined_items[:7]


def format_strategic_evidence_for_prompt(evidence_items):
    blocks = []

    for item in evidence_items:
        block = f"""
Evidence ID: chunk_{item['chunk_id']}
Evidence Category: {item.get('evidence_category', 'General')}
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


def build_valid_evidence_ids(evidence_items):
    valid_ids = []

    for item in evidence_items:
        valid_ids.append(f"chunk_{item['chunk_id']}")

    return ", ".join(valid_ids)


def generate_ceo_answer(question: str, top_k: int = TOP_K):
    evidence_items = retrieve_strategic_evidence(question)

    if not evidence_items:
        return {
            "question": question,
            "answer": "No relevant evidence was found.",
            "evidence": [],
        }

    evidence_context = format_strategic_evidence_for_prompt(evidence_items)
    valid_evidence_ids = build_valid_evidence_ids(evidence_items)

    prompt = build_ceo_prompt(
        question=question,
        evidence_context=evidence_context,
        valid_evidence_ids=valid_evidence_ids,
    )

    llm = load_llm()
    answer = llm.invoke(prompt)

    result = {
        "question": question,
        "answer": answer,
        "evidence": evidence_items,
    }

    return result


def show_ceo_answer(question: str):
    result = generate_ceo_answer(question)

    print("\nAI CEO Strategic Answer")
    print(f"Model: {OLLAMA_MODEL_NAME}")
    print(f"Question: {result['question']}")

    print("\nAnswer:")
    print(result["answer"])

    print("\nEvidence used:")

    for item in result["evidence"]:
        print("\nEvidence ID:", f"chunk_{item['chunk_id']}")
        print("Category:", item.get("evidence_category", "General"))
        print("Title:", item["title"])
        print("Source:", item["source_name"])
        print("Source type:", item["source_type"])
        print("Topic:", item["topic"])
        print("Final score:", item["final_score"])
        print("URL:", item["url"])


def test_rag_chain():
    question = (
        "If you were SAP's CEO today, what strategic action should be "
        "prioritized in Business AI and cloud ERP, and why?"
    )

    show_ceo_answer(question)


if __name__ == "__main__":
    test_rag_chain()