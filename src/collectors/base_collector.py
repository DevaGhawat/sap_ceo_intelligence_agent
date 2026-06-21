import time
from bs4 import BeautifulSoup
import feedparser
import trafilatura

from src.database import insert_document_record
from src.quality_checks import (
    create_content_hash,
    prepare_text_for_storage,
    is_valid_document,
    detect_topic,
    calculate_quality_score,
)


def clean_html_text(text: str) -> str:
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def extract_article_text(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        article_text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )

        if not article_text:
            return ""

        return prepare_text_for_storage(article_text)

    except Exception:
        return ""


def build_raw_text(title: str, summary: str, article_text: str) -> str:
    parts = []

    if title:
        parts.append(title)

    if summary:
        parts.append(summary)

    if article_text:
        parts.append(article_text)

    return prepare_text_for_storage(" ".join(parts))


def collect_from_rss_feed(feed_url: str, source_name: str, source_type: str, limit: int = 20):
    feed = feedparser.parse(feed_url)
    documents = []

    for entry in feed.entries[:limit]:
        title = clean_html_text(entry.get("title", ""))
        summary = clean_html_text(entry.get("summary", ""))
        url = entry.get("link", "")
        published_date = entry.get("published", "")

        article_text = extract_article_text(url)
        raw_text = build_raw_text(title, summary, article_text)

        if not is_valid_document(raw_text):
            continue

        is_full_text = 1 if article_text else 0
        word_count = len(raw_text.split())
        topic = detect_topic(raw_text)
        quality_score = calculate_quality_score(raw_text, source_type, is_full_text)
        content_hash = create_content_hash(raw_text)

        documents.append(
            {
                "title": title,
                "url": url,
                "source_name": source_name,
                "source_type": source_type,
                "topic": topic,
                "published_date": published_date,
                "raw_text": raw_text,
                "content_hash": content_hash,
                "word_count": word_count,
                "quality_score": quality_score,
                "is_full_text": is_full_text,
            }
        )

        time.sleep(0.5)

    return documents


def save_documents(documents):
    inserted_count = 0
    duplicate_count = 0

    for doc in documents:
        inserted = insert_document_record(
            title=doc["title"],
            url=doc["url"],
            source_name=doc["source_name"],
            source_type=doc["source_type"],
            topic=doc["topic"],
            published_date=doc["published_date"],
            raw_text=doc["raw_text"],
            content_hash=doc["content_hash"],
            word_count=doc["word_count"],
            quality_score=doc["quality_score"],
            is_full_text=doc["is_full_text"],
        )

        if inserted:
            inserted_count += 1
        else:
            duplicate_count += 1

    return inserted_count, duplicate_count