from langchain_ollama import OllamaLLM

from src.config import OLLAMA_MODEL_NAME, TOP_K
from src.rag.prompts import build_ceo_prompt
from src.rag.retrieval import retrieve_evidence


def load_llm():
    llm = OllamaLLM(
        model=OLLAMA_MODEL_NAME,
        temperature=0.0,
        num_ctx=3072,
        num_predict=900,
        num_gpu=0,
    )

    return llm


def format_evidence_for_prompt(evidence_items):
    formatted_blocks = []

    for item in evidence_items:
        evidence_id = f"chunk_{item.get('chunk_id')}"
        title = item.get("title", "")
        source_name = item.get("source_name", "")
        source_type = item.get("source_type", "")
        url = item.get("url", "")
        score = item.get("score", item.get("retrieval_score", ""))
        chunk_text = item.get("chunk_text", item.get("text", ""))

        block = f"""
Evidence ID: {evidence_id}
Title: {title}
Source: {source_name}
Source Type: {source_type}
URL: {url}
Retrieval Score: {score}

Text:
{chunk_text}
"""
        formatted_blocks.append(block.strip())

    return "\n\n---\n\n".join(formatted_blocks)


def build_valid_evidence_ids(evidence_items):
    evidence_ids = []

    for item in evidence_items:
        evidence_ids.append(f"chunk_{item.get('chunk_id')}")

    return ", ".join(evidence_ids)


def generate_answer_from_evidence(question, evidence_items):
    if not evidence_items:
        return {
            "answer": "No relevant evidence was retrieved for this question.",
            "evidence_items": [],
            "valid_evidence_ids": "",
        }

    evidence_context = format_evidence_for_prompt(evidence_items)
    valid_evidence_ids = build_valid_evidence_ids(evidence_items)

    prompt = build_ceo_prompt(
        question=question,
        evidence_context=evidence_context,
        valid_evidence_ids=valid_evidence_ids,
    )

    llm = load_llm()
    answer = llm.invoke(prompt)

    return {
        "answer": answer,
        "evidence_items": evidence_items,
        "valid_evidence_ids": valid_evidence_ids,
    }


def generate_ceo_answer(question, top_k=TOP_K):
    evidence_items = retrieve_evidence(question, top_k=top_k)
    result = generate_answer_from_evidence(question, evidence_items)
    return result


def test_rag_chain():
    question = input("Enter CEO question: ").strip()

    if not question:
        print("No question entered.")
        return

    print("\nRunning simple RAG test")
    print(f"Model: {OLLAMA_MODEL_NAME}")
    print(f"Question: {question}")

    result = generate_ceo_answer(question)

    print("\nAnswer")
    print(result["answer"])

    print("\nEvidence IDs")
    print(result["valid_evidence_ids"])


if __name__ == "__main__":
    test_rag_chain()