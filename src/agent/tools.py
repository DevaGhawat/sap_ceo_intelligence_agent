from src.config import TOP_K
from src.rag.retrieval import retrieve_evidence
from src.rag.rag_chain import generate_answer_from_evidence


def get_evidence_id(item):
    return f"chunk_{item.get('chunk_id')}"


def combine_text(item):
    title = item.get("title", "")
    topic = item.get("topic", "")
    source_type = item.get("source_type", "")
    chunk_text = item.get("chunk_text", item.get("text", ""))

    return f"{title} {topic} {source_type} {chunk_text}".lower()


def retrieve_evidence_tool(goal, top_k=TOP_K):
    evidence_items = retrieve_evidence(goal, top_k=top_k)

    return {
        "tool_name": "retrieve_evidence_tool",
        "description": "Retrieves relevant evidence chunks from ChromaDB.",
        "evidence_items": evidence_items,
        "summary": f"Retrieved {len(evidence_items)} evidence chunks.",
    }


def filter_evidence_by_keywords(evidence_items, keywords):
    matched_items = []

    for item in evidence_items:
        text = combine_text(item)

        for keyword in keywords:
            if keyword in text:
                matched_items.append(item)
                break

    return matched_items


def analyze_risks_tool(evidence_items):
    keywords = [
        "risk",
        "challenge",
        "governance",
        "regulation",
        "security",
        "privacy",
        "complexity",
        "migration",
        "fragmented",
        "integration",
        "competition",
    ]

    matched_items = filter_evidence_by_keywords(evidence_items, keywords)

    return {
        "tool_name": "analyze_risks_tool",
        "description": "Analyzes retrieved evidence for risk signals.",
        "count": len(matched_items),
        "evidence_ids": [get_evidence_id(item) for item in matched_items],
        "summary": f"Found {len(matched_items)} possible risk-related evidence items.",
    }


def analyze_opportunities_tool(evidence_items):
    keywords = [
        "opportunity",
        "growth",
        "innovation",
        "automation",
        "business ai",
        "cloud",
        "joule",
        "btp",
        "transformation",
        "productivity",
        "adoption",
    ]

    matched_items = filter_evidence_by_keywords(evidence_items, keywords)

    return {
        "tool_name": "analyze_opportunities_tool",
        "description": "Analyzes retrieved evidence for opportunity signals.",
        "count": len(matched_items),
        "evidence_ids": [get_evidence_id(item) for item in matched_items],
        "summary": f"Found {len(matched_items)} possible opportunity-related evidence items.",
    }


def analyze_trends_tool(evidence_items):
    keywords = [
        "trend",
        "market",
        "enterprise",
        "cloud erp",
        "ai",
        "automation",
        "data",
        "platform",
        "customer",
        "digital transformation",
    ]

    matched_items = filter_evidence_by_keywords(evidence_items, keywords)

    return {
        "tool_name": "analyze_trends_tool",
        "description": "Analyzes retrieved evidence for market and technology trends.",
        "count": len(matched_items),
        "evidence_ids": [get_evidence_id(item) for item in matched_items],
        "summary": f"Found {len(matched_items)} possible trend-related evidence items.",
    }


def generate_recommendation_tool(goal, evidence_items):
    result = generate_answer_from_evidence(goal, evidence_items)

    return {
        "tool_name": "generate_recommendation_tool",
        "description": "Generates CEO-level recommendation using retrieved evidence.",
        "answer": result.get("answer", ""),
        "evidence_items": result.get("evidence_items", evidence_items),
        "valid_evidence_ids": result.get("valid_evidence_ids", ""),
    }