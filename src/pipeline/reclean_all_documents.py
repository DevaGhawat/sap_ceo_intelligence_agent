from src.database import fetch_all_documents, update_cleaned_document, get_repository_statistics
from src.pipeline.preprocess import clean_text


def reclean_all_documents():
    documents = fetch_all_documents()

    updated_count = 0
    skipped_count = 0

    print("\nRe-cleaning all documents")
    print(f"Documents found: {len(documents)}")

    for document in documents:
        doc_id = document["doc_id"]
        raw_text = document["raw_text"]

        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            skipped_count += 1
            continue

        updated = update_cleaned_document(doc_id, cleaned_text)

        if updated:
            updated_count += 1

    stats = get_repository_statistics()

    print("\nRe-cleaning summary")
    print(f"Updated documents: {updated_count}")
    print(f"Skipped documents: {skipped_count}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Clean documents: {stats['clean_documents']}")


if __name__ == "__main__":
    reclean_all_documents()