from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.database import (
    fetch_clean_documents,
    clear_chunks,
    insert_chunk_record,
    get_repository_statistics,
)


def create_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def split_document_text(text: str):
    splitter = create_text_splitter()
    chunks = splitter.split_text(text)

    clean_chunks = []

    for chunk in chunks:
        chunk = chunk.strip()

        if chunk:
            clean_chunks.append(chunk)

    return clean_chunks


def create_chunks_for_document(document):
    doc_id = document["doc_id"]
    cleaned_text = document["cleaned_text"]

    chunks = split_document_text(cleaned_text)
    inserted_count = 0

    for index, chunk_text in enumerate(chunks):
        word_count = len(chunk_text.split())

        inserted = insert_chunk_record(
            doc_id=doc_id,
            chunk_index=index,
            chunk_text=chunk_text,
            word_count=word_count,
        )

        if inserted:
            inserted_count += 1

    return inserted_count


def build_chunks():
    clear_chunks()

    documents = fetch_clean_documents()

    total_chunks = 0

    print("\nStarting chunking")
    print(f"Clean documents: {len(documents)}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Chunk overlap: {CHUNK_OVERLAP}")

    for document in documents:
        chunk_count = create_chunks_for_document(document)
        total_chunks += chunk_count

    stats = get_repository_statistics()

    print("\nChunking summary")
    print(f"Documents processed: {len(documents)}")
    print(f"Chunks created: {total_chunks}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total chunks: {stats['total_chunks']}")


if __name__ == "__main__":
    build_chunks()