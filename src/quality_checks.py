import hashlib
import re

from src.config import REJECTED_TEXT_MARKERS, COMPANY_RELEVANT_TERMS


def create_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def normalize_spaces(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_blocked_or_cookie_text(text: str) -> bool:
    if not text:
        return True

    lower_text = text.lower()

    for marker in REJECTED_TEXT_MARKERS:
        if marker in lower_text:
            return True

    return False


def is_company_relevant(text: str) -> bool:
    if not text:
        return False

    lower_text = text.lower()

    for term in COMPANY_RELEVANT_TERMS:
        if term in lower_text:
            return True

    return False


def detect_topic(text: str) -> str:
    lower_text = text.lower()

    topic_keywords = {
        "risk": [
            "risk",
            "challenge",
            "pressure",
            "slowdown",
            "decline",
            "uncertainty",
            "customer resistance",
            "implementation complexity",
        ],
        "opportunity": [
            "opportunity",
            "growth",
            "demand",
            "expansion",
            "adoption",
            "transformation",
            "new market",
        ],
        "competitor": [
            "oracle",
            "microsoft",
            "salesforce",
            "workday",
            "servicenow",
            "dynamics",
            "netsuite",
        ],
        "technology": [
            "ai",
            "business ai",
            "joule",
            "cloud erp",
            "s/4hana",
            "sap hana",
            "btp",
            "automation",
            "analytics",
        ],
        "regulation": [
            "regulation",
            "compliance",
            "privacy",
            "data protection",
            "gdpr",
            "ai act",
            "security",
        ],
        "financial": [
            "revenue",
            "earnings",
            "profit",
            "margin",
            "forecast",
            "investor",
            "cloud revenue",
        ],
        "partnership": [
            "partner",
            "partnership",
            "collaboration",
            "deal",
            "alliance",
            "microsoft",
            "google cloud",
            "aws",
        ],
        "sentiment": [
            "reddit",
            "community",
            "customer",
            "developer",
            "user feedback",
            "discussion",
        ],
    }

    scores = {}

    for topic, keywords in topic_keywords.items():
        score = 0

        for keyword in keywords:
            if keyword in lower_text:
                score += 1

        scores[topic] = score

    best_topic = max(scores, key=scores.get)

    if scores[best_topic] == 0:
        return "general"

    return best_topic


def guess_is_full_text(text: str) -> int:
    word_count = len(text.split())

    if word_count >= 250:
        return 1

    return 0


def calculate_quality_score(text: str, source_type: str, is_full_text: int) -> int:
    score = 0
    word_count = len(text.split())

    if word_count >= 700:
        score += 35
    elif word_count >= 300:
        score += 28
    elif word_count >= 100:
        score += 20
    else:
        score += 10

    if source_type in ["official", "technical", "financial"]:
        score += 30
    elif source_type == "news":
        score += 20
    elif source_type == "community":
        score += 10

    lower_text = text.lower()

    if "sap" in lower_text:
        score += 20

    if is_full_text == 1:
        score += 15

    return min(score, 100)


def is_valid_document(text: str) -> bool:
    text = normalize_spaces(text)

    if not text:
        return False

    if is_blocked_or_cookie_text(text):
        return False

    if not is_company_relevant(text):
        return False

    return True


def prepare_text_for_storage(text: str) -> str:
    return normalize_spaces(text)


def test_quality_checks():
    sample_text = """
    SAP announced new Business AI features for cloud ERP customers.
    The company is expanding Joule and SAP Business Technology Platform
    to support enterprise automation and digital transformation.
    """

    text = prepare_text_for_storage(sample_text)
    topic = detect_topic(text)
    is_full_text = guess_is_full_text(text)
    quality_score = calculate_quality_score(text, "official", is_full_text)
    content_hash = create_content_hash(text)

    print("Quality check test")
    print(f"Valid document: {is_valid_document(text)}")
    print(f"Topic: {topic}")
    print(f"Word count: {len(text.split())}")
    print(f"Is full text: {is_full_text}")
    print(f"Quality score: {quality_score}")
    print(f"Content hash sample: {content_hash[:12]}")


if __name__ == "__main__":
    test_quality_checks()