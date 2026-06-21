from src.dashboard.dashboard_utils import *


def show_project_pipeline():
    st.header("Project Pipeline")

    st.write(
        "This section gives a quick overview of how the system collects information, "
        "stores it, retrieves evidence, and generates CEO-level recommendations."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Documents", 239)

    with col2:
        st.metric("Sources", 6)

    with col3:
        st.metric("Chunks", 3398)

    with col4:
        st.metric("LLM", "Qwen3:8B")

    st.subheader("Architecture at a Glance")

    st.code(
        "Public Sources → SQLite → Preprocessing → Chunking → Embeddings → "
        "ChromaDB → RAG Retrieval → Qwen3:8B → Streamlit Dashboard",
        language="text",
    )

    st.subheader("Main Pipeline Stages")

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        st.markdown(
            """
            <div class="dashboard-card">
            <b>1. Data Collection</b><br><br>
            Collects public SAP, financial, technical, and external market information.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with row1_col2:
        st.markdown(
            """
            <div class="dashboard-card">
            <b>2. Knowledge Repository</b><br><br>
            Stores documents, metadata, source details, quality scores, and cleaned text in SQLite.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with row1_col3:
        st.markdown(
            """
            <div class="dashboard-card">
            <b>3. Text Processing</b><br><br>
            Cleans raw web text, removes noise, handles duplicates, and prepares text for NLP.
            </div>
            """,
            unsafe_allow_html=True,
        )

    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        st.markdown(
            """
            <div class="dashboard-card">
            <b>4. Chunking and Embeddings</b><br><br>
            Splits documents into chunks and converts them into semantic vectors using all-MiniLM-L6-v2.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with row2_col2:
        st.markdown(
            """
            <div class="dashboard-card">
            <b>5. Retrieval</b><br><br>
            Searches ChromaDB to retrieve the most relevant evidence chunks for a CEO-level question.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with row2_col3:
        st.markdown(
            """
            <div class="dashboard-card">
            <b>6. CEO Recommendation</b><br><br>
            Uses Qwen3:8B through Ollama to generate evidence-based strategic recommendations.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Why RAG is used")

    st.write(
        "RAG keeps the system grounded in collected evidence. Instead of allowing the LLM to answer "
        "only from general knowledge, the system first retrieves relevant evidence from ChromaDB and "
        "then generates a recommendation using that evidence."
    )

    st.caption(
        "Detailed architecture, technology stack, design decisions, and requirement mapping are included in the README file."
    )