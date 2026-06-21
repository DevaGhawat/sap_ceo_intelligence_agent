import re
from html import unescape
from bs4 import BeautifulSoup

from src.database import (
    fetch_documents_for_preprocessing,
    update_cleaned_document,
    get_repository_statistics,
)

def remove_html_tags(text: str) -> str:
    text = unescape(text)
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    return text


def normalize_spaces(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_web_noise(text: str) -> str:
    noise_patterns = [
        r"Subscribe to.*",
        r"Sign up for.*",
        r"All rights reserved.*",
        r"Cookie Policy.*",
        r"Privacy Policy.*",
        r"Terms of Use.*",
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    return text


def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = raw_text
    text = remove_html_tags(text)
    text = remove_web_noise(text)
    text = normalize_spaces(text)

    return text


def preprocess_documents():
    documents = fetch_documents_for_preprocessing()

    processed_count = 0
    skipped_count = 0

    print("\nStarting preprocessing")
    print(f"Documents to process: {len(documents)}")

    for document in documents:
        doc_id = document["doc_id"]
        raw_text = document["raw_text"]

        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            skipped_count += 1
            continue

        updated = update_cleaned_document(doc_id, cleaned_text)

        if updated:
            processed_count += 1

    stats = get_repository_statistics()

    print("\nPreprocessing summary")
    print(f"Processed documents: {processed_count}")
    print(f"Skipped documents: {skipped_count}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Clean documents: {stats['clean_documents']}")


if __name__ == "__main__":
    preprocess_documents()