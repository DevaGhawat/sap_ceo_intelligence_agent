import streamlit as st

from src.dashboard.dashboard_utils import show_header, apply_dashboard_style
from src.dashboard.company_overview_tab import show_company_overview
from src.dashboard.market_intelligence_tab import show_market_intelligence
from src.dashboard.opportunity_monitor_tab import show_opportunity_monitor
from src.dashboard.risk_monitor_tab import show_risk_monitor
from src.dashboard.sentiment_analysis_tab import show_sentiment_analysis
from src.dashboard.strategic_recommendations_tab import show_strategic_recommendations
from src.dashboard.ceo_briefing_tab import show_ceo_briefing
from src.dashboard.project_pipeline_tab import show_project_pipeline


def main():
    st.set_page_config(
        page_title="SAP AI CEO Strategic Intelligence",
        page_icon="📊",
        layout="wide"
    )

    apply_dashboard_style()
    show_header()

    st.sidebar.title("SAP AI CEO Agent")
    st.sidebar.caption("Executive Strategic Intelligence Dashboard")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Project Snapshot**")
    st.sidebar.markdown(
        """
        - **Company:** SAP
        - **Documents:** 239
        - **Sources:** 6
        - **Chunks:** 3398
        - **LLM:** Qwen3:8B
        - **Vector DB:** ChromaDB
        """
    )

    st.sidebar.markdown("---")

    section_names = [
        "Company Overview",
        "Market Intelligence",
        "Opportunity Monitor",
        "Risk Monitor",
        "Sentiment Analysis",
        "Strategic Recommendations",
        "CEO Briefing",
        "Project Pipeline",
    ]

    section_labels = {
        "Company Overview": "1. Company Overview",
        "Market Intelligence": "2. Market Intelligence",
        "Opportunity Monitor": "3. Opportunity Monitor",
        "Risk Monitor": "4. Risk Monitor",
        "Sentiment Analysis": "5. Sentiment Analysis",
        "Strategic Recommendations": "6. Strategic Recommendations",
        "CEO Briefing": "7. CEO Briefing",
        "Project Pipeline": "8. Project Pipeline",
    }

    selected_section = st.sidebar.radio(
        "Dashboard Sections",
        section_names,
        format_func=lambda section: section_labels[section],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Pipeline: Collection → SQLite → Cleaning → Chunking → Embeddings → ChromaDB → RAG → Dashboard"
    )

    if selected_section == "Company Overview":
        show_company_overview()
    elif selected_section == "Market Intelligence":
        show_market_intelligence()
    elif selected_section == "Opportunity Monitor":
        show_opportunity_monitor()
    elif selected_section == "Risk Monitor":
        show_risk_monitor()
    elif selected_section == "Sentiment Analysis":
        show_sentiment_analysis()
    elif selected_section == "Strategic Recommendations":
        show_strategic_recommendations()
    elif selected_section == "CEO Briefing":
        show_ceo_briefing()
    elif selected_section == "Project Pipeline":
        show_project_pipeline()


if __name__ == "__main__":
    main()