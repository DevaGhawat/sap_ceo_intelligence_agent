import sqlite3
from datetime import datetime
from typing import Optional

from src.config import DATABASE_PATH, create_project_folders


def open_database_connection():
    create_project_folders()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def create_database_schema():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            source_name TEXT,
            source_type TEXT,
            topic TEXT,
            published_date TEXT,
            collected_at TEXT,
            raw_text TEXT,
            cleaned_text TEXT,
            word_count INTEGER,
            quality_score INTEGER,
            is_full_text INTEGER,
            content_hash TEXT UNIQUE,
            processed_status TEXT DEFAULT 'raw'
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            chunk_index INTEGER,
            chunk_text TEXT,
            word_count INTEGER,
            embedding_status TEXT DEFAULT 'pending',
            FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            evidence_summary TEXT,
            created_at TEXT
        )
        """
    )

    connection.commit()
    connection.close()

    print("Database schema created successfully.")


def insert_document_record(
    title: str,
    url: str,
    source_name: str,
    source_type: str,
    topic: str,
    published_date: str,
    raw_text: str,
    content_hash: str,
    word_count: int,
    quality_score: int,
    is_full_text: int,
) -> bool:
    connection = open_database_connection()
    cursor = connection.cursor()

    collected_at = datetime.now().isoformat(timespec="seconds")

    try:
        cursor.execute(
            """
            INSERT INTO documents (
                title,
                url,
                source_name,
                source_type,
                topic,
                published_date,
                collected_at,
                raw_text,
                cleaned_text,
                word_count,
                quality_score,
                is_full_text,
                content_hash,
                processed_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                url,
                source_name,
                source_type,
                topic,
                published_date,
                collected_at,
                raw_text,
                None,
                word_count,
                quality_score,
                is_full_text,
                content_hash,
                "raw",
            ),
        )

        connection.commit()
        inserted = True

    except sqlite3.IntegrityError:
        inserted = False

    finally:
        connection.close()

    return inserted


def fetch_all_documents(limit: Optional[int] = None):
    connection = open_database_connection()
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM documents
        ORDER BY doc_id DESC
    """

    if limit is not None:
        query += f" LIMIT {int(limit)}"

    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def fetch_documents_for_preprocessing():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE processed_status = 'raw'
        ORDER BY doc_id ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def update_cleaned_document(doc_id: int, cleaned_text: str) -> bool:
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE documents
        SET cleaned_text = ?,
            processed_status = 'cleaned'
        WHERE doc_id = ?
        """,
        (cleaned_text, doc_id),
    )

    connection.commit()
    updated = cursor.rowcount > 0
    connection.close()

    return updated


def fetch_clean_documents():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE cleaned_text IS NOT NULL
          AND cleaned_text != ''
        ORDER BY doc_id ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def clear_chunks():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM chunks")

    connection.commit()
    connection.close()

    print("Old chunks removed.")


def insert_chunk_record(
    doc_id: int,
    chunk_index: int,
    chunk_text: str,
    word_count: int,
) -> bool:
    connection = open_database_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO chunks (
                doc_id,
                chunk_index,
                chunk_text,
                word_count,
                embedding_status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                chunk_index,
                chunk_text,
                word_count,
                "pending",
            ),
        )

        connection.commit()
        inserted = True

    except sqlite3.IntegrityError:
        inserted = False

    finally:
        connection.close()

    return inserted


def fetch_all_chunks():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            chunks.chunk_id,
            chunks.doc_id,
            chunks.chunk_index,
            chunks.chunk_text,
            chunks.word_count,
            documents.title,
            documents.url,
            documents.source_name,
            documents.source_type,
            documents.topic,
            documents.published_date,
            documents.quality_score,
            documents.is_full_text
        FROM chunks
        JOIN documents
            ON chunks.doc_id = documents.doc_id
        ORDER BY chunks.chunk_id ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def insert_recommendation_record(
    question: str,
    answer: str,
    evidence_summary: str,
) -> bool:
    connection = open_database_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute(
        """
        INSERT INTO recommendations (
            question,
            answer,
            evidence_summary,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            question,
            answer,
            evidence_summary,
            created_at,
        ),
    )

    connection.commit()
    connection.close()

    return True


def get_repository_statistics():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total_documents = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM documents
        WHERE cleaned_text IS NOT NULL
          AND cleaned_text != ''
        """
    )
    clean_documents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chunks")
    total_chunks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT source_name) FROM documents")
    distinct_sources = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(word_count) FROM documents")
    average_word_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(quality_score) FROM documents")
    average_quality_score = cursor.fetchone()[0]

    connection.close()

    return {
        "total_documents": total_documents,
        "clean_documents": clean_documents,
        "total_chunks": total_chunks,
        "distinct_sources": distinct_sources,
        "average_word_count": round(average_word_count or 0, 2),
        "average_quality_score": round(average_quality_score or 0, 2),
    }


def show_repository_statistics():
    stats = get_repository_statistics()

    print("\nRepository Statistics")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Clean documents: {stats['clean_documents']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Distinct sources: {stats['distinct_sources']}")
    print(f"Average word count: {stats['average_word_count']}")
    print(f"Average quality score: {stats['average_quality_score']}")


def show_source_type_counts():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT source_type, COUNT(*)
        FROM documents
        GROUP BY source_type
        ORDER BY COUNT(*) DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    print("\nSource Type Counts")

    if not rows:
        print("No documents found yet.")

    for row in rows:
        print(f"{row[0]}: {row[1]}")


def show_topic_counts():
    connection = open_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT topic, COUNT(*)
        FROM documents
        GROUP BY topic
        ORDER BY COUNT(*) DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    print("\nTopic Counts")

    if not rows:
        print("No documents found yet.")

    for row in rows:
        print(f"{row[0]}: {row[1]}")


if __name__ == "__main__":
    create_database_schema()
    show_repository_statistics()
    show_source_type_counts()
    show_topic_counts()