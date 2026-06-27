# Shared dashboard utilities and data loading functions

import sqlite3
import re
import pandas as pd
import plotly.express as px
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.config import COMPANY_NAME, DATABASE_PATH
from src.database import get_repository_statistics
from src.agent.ceo_agent import run_ceo_agent
COMPETITOR_TERMS = [
    "oracle",
    "microsoft dynamics",
    "microsoft",
    "salesforce",
    "workday",
    "servicenow",
    "infor",
    "epicor",
    "netsuite",
]
TECHNOLOGY_TERMS = [
    "business ai",
    "generative ai",
    "agentic ai",
    "joule",
    "sap btp",
    "business technology platform",
    "cloud erp",
    "autonomous enterprise",
    "ai agents",
    "data cloud",
]
ANNOUNCEMENT_TERMS = [
    "launch",
    "announces",
    "announced",
    "unveils",
    "release",
    "sapphire",
    "partnership",
    "offering",
]


def run_query(query, params=None):
    connection = sqlite3.connect(DATABASE_PATH)

    if params is None:
        params = []

    df = pd.read_sql_query(query, connection, params=params)
    connection.close()

    return df


def load_source_type_counts():
    query = """
    SELECT source_type, COUNT(*) AS document_count
    FROM documents
    GROUP BY source_type
    ORDER BY document_count DESC
    """

    return run_query(query)


def load_source_name_counts():
    query = """
    SELECT source_name, source_type, COUNT(*) AS document_count
    FROM documents
    GROUP BY source_name, source_type
    ORDER BY document_count DESC
    """

    return run_query(query)


def load_topic_counts():
    query = """
    SELECT topic, COUNT(*) AS document_count
    FROM documents
    GROUP BY topic
    ORDER BY document_count DESC
    """

    return run_query(query)


def load_quality_summary():
    query = """
    SELECT
        source_type,
        COUNT(*) AS document_count,
        ROUND(AVG(word_count), 2) AS avg_word_count,
        ROUND(AVG(quality_score), 2) AS avg_quality_score
    FROM documents
    GROUP BY source_type
    ORDER BY document_count DESC
    """

    return run_query(query)


def get_distinct_source_count():
    query = """
    SELECT COUNT(DISTINCT source_name) AS source_count
    FROM documents
    """

    df = run_query(query)

    if df.empty:
        return 0

    return int(df["source_count"].iloc[0])


def get_last_update_timestamp():
    query = """
    SELECT MAX(collected_at) AS last_update
    FROM documents
    """

    df = run_query(query)

    if df.empty or pd.isna(df["last_update"].iloc[0]):
        return "Not available"

    return str(df["last_update"].iloc[0])


def count_documents_by_topic(topic_name):
    query = """
    SELECT COUNT(*) AS total_count
    FROM documents
    WHERE topic = ?
    """

    df = run_query(query, [topic_name])

    return int(df["total_count"].iloc[0])


def get_average_quality_by_topic(topic_name):
    query = """
    SELECT ROUND(AVG(quality_score), 2) AS avg_quality
    FROM documents
    WHERE topic = ?
    """

    df = run_query(query, [topic_name])

    if df.empty or pd.isna(df["avg_quality"].iloc[0]):
        return 0

    return float(df["avg_quality"].iloc[0])


def load_documents_by_topic(topic_name, limit=None):
    query = """
    SELECT
        doc_id,
        title,
        source_name,
        source_type,
        topic,
        published_date,
        collected_at,
        word_count,
        quality_score,
        url,
        cleaned_text
    FROM documents
    WHERE topic = ?
    ORDER BY quality_score DESC, word_count DESC
    """

    params = [topic_name]

    if limit is not None:
        query = query + " LIMIT ?"
        params.append(limit)

    df = run_query(query, params)

    if not df.empty:
        df["preview"] = df["cleaned_text"].fillna("").str.slice(0, 350)

    return df


def load_recent_documents(limit=None):
    query = """
    SELECT
        doc_id,
        title,
        source_name,
        source_type,
        topic,
        published_date,
        collected_at,
        word_count,
        quality_score,
        url,
        cleaned_text
    FROM documents
    ORDER BY collected_at DESC, quality_score DESC
    """

    params = []

    if limit is not None:
        query = query + " LIMIT ?"
        params.append(limit)

    df = run_query(query, params)

    if not df.empty:
        df["preview"] = df["cleaned_text"].fillna("").str.slice(0, 280)

    return df


def load_documents_matching_terms(terms, limit=None):
    conditions = []
    params = []

    for term in terms:
        search_term = f"%{term.lower()}%"
        conditions.append(
            """
            (
                LOWER(COALESCE(title, '')) LIKE ?
                OR LOWER(COALESCE(cleaned_text, '')) LIKE ?
            )
            """
        )
        params.append(search_term)
        params.append(search_term)

    where_clause = " OR ".join(conditions)

    query = f"""
    SELECT
        doc_id,
        title,
        source_name,
        source_type,
        topic,
        published_date,
        collected_at,
        word_count,
        quality_score,
        url,
        cleaned_text
    FROM documents
    WHERE {where_clause}
    ORDER BY quality_score DESC, word_count DESC
    """

    if limit is not None:
        query = query + " LIMIT ?"
        params.append(limit)

    df = run_query(query, params)

    if not df.empty:
        df["preview"] = df["cleaned_text"].fillna("").str.slice(0, 300)

    return df


def load_announcements(limit=None):
    announcement_df = load_documents_matching_terms(ANNOUNCEMENT_TERMS, limit=None)

    if announcement_df.empty:
        return announcement_df

    announcement_df = announcement_df[
        announcement_df["source_type"].isin(["official", "technical", "financial"])
    ]

    if limit is not None:
        announcement_df = announcement_df.head(limit)

    return announcement_df


def load_all_documents_for_sentiment():
    query = """
    SELECT
        doc_id,
        title,
        source_name,
        source_type,
        topic,
        quality_score,
        published_date,
        collected_at,
        url,
        cleaned_text
    FROM documents
    WHERE cleaned_text IS NOT NULL
    """

    return run_query(query)


def classify_sentiment(score):
    if score >= 0.20:
        return "positive"

    if score <= -0.20:
        return "negative"

    return "neutral"


def prepare_text_for_sentiment(title, text, max_chars=1800):
    title = str(title)
    text = str(text)

    text = re.sub(r"\s+", " ", text).strip()
    text = text[:max_chars]

    return f"{title}. {text}"


def calculate_sentence_average_sentiment(analyzer, text):
    sentences = re.split(r"(?<=[.!?])\s+", text)

    clean_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence.split()) >= 4:
            clean_sentences.append(sentence)

    if not clean_sentences:
        return analyzer.polarity_scores(text)["compound"]

    sentence_scores = []

    for sentence in clean_sentences[:25]:
        score = analyzer.polarity_scores(sentence)["compound"]
        sentence_scores.append(score)

    if not sentence_scores:
        return 0

    average_score = sum(sentence_scores) / len(sentence_scores)

    return average_score


def parse_document_date(published_date, collected_at):
    published_datetime = pd.to_datetime(
        published_date,
        errors="coerce",
        utc=True,
    )

    if not pd.isna(published_datetime):
        return published_datetime.date(), "published_date"

    collected_datetime = pd.to_datetime(
        collected_at,
        errors="coerce",
        utc=True,
    )

    if not pd.isna(collected_datetime):
        return collected_datetime.date(), "collected_at"

    return None, "not_available"


def build_sentiment_dataframe():
    df = load_all_documents_for_sentiment()

    analyzer = SentimentIntensityAnalyzer()
    sentiment_rows = []

    for _, row in df.iterrows():
        sentiment_text = prepare_text_for_sentiment(
            row["title"],
            row["cleaned_text"],
        )

        score = calculate_sentence_average_sentiment(
            analyzer,
            sentiment_text,
        )

        label = classify_sentiment(score)

        sentiment_date, date_source = parse_document_date(
            row["published_date"],
            row["collected_at"],
        )

        sentiment_rows.append(
            {
                "doc_id": row["doc_id"],
                "title": row["title"],
                "source_name": row["source_name"],
                "source_type": row["source_type"],
                "topic": row["topic"],
                "quality_score": row["quality_score"],
                "published_date": row["published_date"],
                "collected_at": row["collected_at"],
                "sentiment_date": sentiment_date,
                "date_source": date_source,
                "sentiment_score": round(score, 4),
                "sentiment_label": label,
                "url": row["url"],
            }
        )

    sentiment_df = pd.DataFrame(sentiment_rows)

    return sentiment_df


def get_confidence_label(quality_score):
    if quality_score >= 90:
        return "High"

    if quality_score >= 70:
        return "Medium"

    return "Low"


def get_impact_level(row):
    text = f"{row['title']} {row.get('preview', '')}".lower()
    quality_score = row["quality_score"]

    strong_terms = [
        "growth",
        "launch",
        "platform",
        "business ai",
        "cloud erp",
        "customer",
        "partnership",
        "autonomous enterprise",
        "joule",
    ]

    if quality_score >= 90 and any(term in text for term in strong_terms):
        return "High"

    if quality_score >= 70:
        return "Medium"

    return "Low"


def get_risk_category(row):
    text = f"{row['title']} {row.get('preview', '')}".lower()

    if "governance" in text or "compliance" in text or "audit" in text:
        return "AI Governance / Compliance"

    if "fragmented" in text or "data" in text or "silo" in text:
        return "Data Fragmentation"

    if "implementation" in text or "complexity" in text or "migration" in text:
        return "Implementation Complexity"

    if "competitor" in text or "competition" in text or "market pressure" in text:
        return "Competitive / Market Risk"

    if "supply chain" in text or "operational" in text:
        return "Operational Risk"

    return "Strategic Risk"


def get_severity_level(row):
    text = f"{row['title']} {row.get('preview', '')}".lower()
    quality_score = row["quality_score"]

    high_risk_terms = [
        "risk",
        "governance",
        "fragmented",
        "complexity",
        "disruption",
        "compliance",
        "audit",
        "pressure",
        "challenge",
    ]

    if quality_score >= 90 and any(term in text for term in high_risk_terms):
        return "High"

    if quality_score >= 70:
        return "Medium"

    return "Low"


def prepare_opportunity_table(df):
    if df.empty:
        return df

    rows = []

    for _, row in df.iterrows():
        rows.append(
            {
                "Opportunity Title": row["title"],
                "Impact Level": get_impact_level(row),
                "Evidence": row["preview"],
                "Confidence Score": round(float(row["quality_score"]), 2),
                "Confidence Label": get_confidence_label(row["quality_score"]),
                "Source": row["source_name"],
                "Source Type": row["source_type"],
                "URL": row["url"],
            }
        )

    return pd.DataFrame(rows)


def prepare_risk_table(df):
    if df.empty:
        return df

    rows = []

    for _, row in df.iterrows():
        rows.append(
            {
                "Risk Title": row["title"],
                "Risk Category": get_risk_category(row),
                "Severity Level": get_severity_level(row),
                "Evidence": row["preview"],
                "Confidence Score": round(float(row["quality_score"]), 2),
                "Confidence Label": get_confidence_label(row["quality_score"]),
                "Source": row["source_name"],
                "Source Type": row["source_type"],
                "URL": row["url"],
            }
        )

    risk_table = pd.DataFrame(rows)

    severity_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    risk_table["Severity Priority"] = risk_table["Severity Level"].map(severity_order)

    risk_table = risk_table.sort_values(
        by=["Severity Priority", "Confidence Score"],
        ascending=[True, False]
    )

    risk_table = risk_table.drop(columns=["Severity Priority"])

    return risk_table


def prepare_market_table(df, title_column_name):
    if df.empty:
        return df

    display_df = df[
        [
            "title",
            "source_name",
            "source_type",
            "topic",
            "published_date",
            "collected_at",
            "quality_score",
            "url",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "title": title_column_name,
            "source_name": "Source",
            "source_type": "Source Type",
            "topic": "Topic",
            "published_date": "Published Date",
            "collected_at": "Collected At",
            "quality_score": "Confidence Score",
            "url": "URL",
        }
    )

    return display_df


def identify_competitors(row):
    text = f"{row['title']} {row.get('cleaned_text', '')}".lower()

    found_competitors = []

    competitor_map = {
        "oracle": "Oracle",
        "microsoft dynamics": "Microsoft Dynamics",
        "microsoft": "Microsoft",
        "salesforce": "Salesforce",
        "workday": "Workday",
        "servicenow": "ServiceNow",
        "infor": "Infor",
        "epicor": "Epicor",
        "netsuite": "NetSuite",
    }

    for term, display_name in competitor_map.items():
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text):
            found_competitors.append(display_name)

    if not found_competitors:
        return "Not clearly identified"

    return ", ".join(sorted(set(found_competitors)))


def prepare_competitor_table(df):
    if df.empty:
        return df

    rows = []

    for _, row in df.iterrows():
        rows.append(
            {
                "Competitor Activity Title": row["title"],
                "Detected Competitor": identify_competitors(row),
                "Source": row["source_name"],
                "Source Type": row["source_type"],
                "Topic": row["topic"],
                "Published Date": row["published_date"],
                "Collected At": row["collected_at"],
                "Confidence Score": row["quality_score"],
                "URL": row["url"],
            }
        )
    competitor_table = pd.DataFrame(rows)

    competitor_table = competitor_table[
        competitor_table["Detected Competitor"] != "Not clearly identified"
    ]

    competitor_table["Source Priority"] = competitor_table["Source Type"].apply(
        lambda source_type: 0 if source_type == "external_news" else 1
    )

    competitor_table = competitor_table.sort_values(
        by=["Source Priority", "Confidence Score"],
        ascending=[True, False]
    )

    competitor_table = competitor_table.drop(columns=["Source Priority"])

    return competitor_table


def show_header():
    st.title("SAP AI CEO Strategic Intelligence Agent")

    st.write(
        "An NLP and Retrieval-Augmented Generation system that collects SAP-related public information, "
        "stores it in a knowledge repository, retrieves strategic evidence, and generates CEO-level recommendations."
    )


def show_repository_metrics():
    stats = get_repository_statistics()
    source_count = get_distinct_source_count()
    last_update = get_last_update_timestamp()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Company", COMPANY_NAME)
    col2.metric("Documents", stats["total_documents"])
    col3.metric("Data Sources", source_count)
    col4.metric("Clean Documents", stats["clean_documents"])
    col5.metric("Chunks", stats["total_chunks"])
    col6.metric("Avg Quality", stats["average_quality_score"])

    st.caption(f"Last update timestamp: {last_update}")


def show_repository_charts():
    source_df = load_source_type_counts()
    source_name_df = load_source_name_counts()
    topic_df = load_topic_counts()
    quality_df = load_quality_summary()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Source Type Distribution")
        fig = px.bar(
            source_df,
            x="source_type",
            y="document_count",
            text="document_count",
            title="Documents by Source Type",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Topic Distribution")
        fig = px.bar(
            topic_df,
            x="topic",
            y="document_count",
            text="document_count",
            title="Documents by Topic",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Sources")
    st.dataframe(source_name_df, use_container_width=True)

    st.subheader("Quality Summary")
    st.dataframe(quality_df, use_container_width=True)


def build_evidence_dataframe(result):
    evidence_rows = []

    for item in result["evidence"]:
        evidence_rows.append(
            {
                "Evidence ID": f"chunk_{item['chunk_id']}",
                "Category": item.get("evidence_category", "General"),
                "Title": item["title"],
                "Source": item["source_name"],
                "Source Type": item["source_type"],
                "Topic": item["topic"],
                "Final Score": item["final_score"],
                "URL": item["url"],
            }
        )

    return pd.DataFrame(evidence_rows)


def show_evidence_preview(result):
    st.subheader("Evidence Text Preview")

    for item in result["evidence"]:
        title = item["title"]
        chunk_id = item["chunk_id"]
        category = item.get("evidence_category", "General")

        with st.expander(f"chunk_{chunk_id} | {category} | {title}"):
            st.write(item["text"])
            st.write("Source:", item["source_name"])
            st.write("Source Type:", item["source_type"])
            st.write("URL:", item["url"])
            
            
            
def apply_dashboard_style():
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 16px 18px;
            border-radius: 12px;
            text-align: center !important;
        }

        div[data-testid="stMetric"] > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }

        div[data-testid="stMetricLabel"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            text-align: center !important;
        }

        div[data-testid="stMetricLabel"] > div {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            text-align: center !important;
        }

        div[data-testid="stMetricLabel"] p {
            width: 100% !important;
            text-align: center !important;
            margin: 0 auto !important;
        }

        div[data-testid="stMetricValue"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            text-align: center !important;
        }

        div[data-testid="stMetricValue"] > div {
            width: 100% !important;
            text-align: center !important;
        }

        .section-note {
            background-color: rgba(255, 255, 255, 0.04);
            border-left: 4px solid #7c3aed;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        .small-muted {
            opacity: 0.75;
            font-size: 0.9rem;
        }

        .dashboard-card {
            background-color: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 14px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )