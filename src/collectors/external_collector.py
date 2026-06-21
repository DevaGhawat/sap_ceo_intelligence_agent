from src.collectors.base_collector import collect_from_rss_feed, save_documents
from src.database import show_repository_statistics, show_source_type_counts


def get_external_feeds():
    feeds = [
        {
            "feed_url": "https://www.techtarget.com/searchsap/rss/SAP-news-tips-and-expert-advice.xml",
            "source_name": "TechTarget SearchSAP",
        },
        {
            "feed_url": "https://www.techtarget.com/searcherp/rss/SearchERP-RSS.xml",
            "source_name": "TechTarget SearchERP",
        },
        {
            "feed_url": "https://www.ciodive.com/feeds/news/",
            "source_name": "CIO Dive",
        },
    ]

    return feeds


def collect_external_documents():
    all_documents = []

    feeds = get_external_feeds()

    print("\nStarting external source collection")

    for feed in feeds:
        print("\nCollecting from:", feed["source_name"])

        documents = collect_from_rss_feed(
            feed_url=feed["feed_url"],
            source_name=feed["source_name"],
            source_type="external_news",
            limit=50,
        )

        print("Documents collected from feed:", len(documents))
        all_documents.extend(documents)

    print("\nExternal collection summary")
    print("Total external documents collected:", len(all_documents))

    inserted_count, duplicate_count = save_documents(all_documents)

    print("Inserted documents:", inserted_count)
    print("Duplicates skipped:", duplicate_count)

    show_repository_statistics()
    show_source_type_counts()


if __name__ == "__main__":
    collect_external_documents()