from src.database import create_database_schema, get_repository_statistics
from src.collectors.base_collector import collect_from_rss_feed, save_documents


def get_official_feeds():
    feeds = [
        "https://news.sap.com/feed/",
        "https://news.sap.com/topics/business-ai/feed/",
        "https://news.sap.com/topics/cloud/feed/",
        "https://news.sap.com/topics/sap-sapphire/feed/",
        "https://news.sap.com/topics/technology/feed/",
    ]

    return feeds


def collect_official_documents():
    create_database_schema()

    all_documents = []
    feeds = get_official_feeds()

    print("\nCollecting SAP official documents")

    for feed_url in feeds:
        print(f"Feed: {feed_url}")

        documents = collect_from_rss_feed(
            feed_url=feed_url,
            source_name="SAP News Center",
            source_type="official",
            limit=25,
        )

        print(f"Useful documents: {len(documents)}")
        all_documents.extend(documents)

    inserted_count, duplicate_count = save_documents(all_documents)
    stats = get_repository_statistics()

    print("\nOfficial collection summary")
    print(f"Collected documents: {len(all_documents)}")
    print(f"Inserted documents: {inserted_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    print(f"Total documents in database: {stats['total_documents']}")
    print(f"Average word count: {stats['average_word_count']}")
    print(f"Average quality score: {stats['average_quality_score']}")


if __name__ == "__main__":
    collect_official_documents()