from src.dashboard.dashboard_utils import *


def show_market_intelligence():
    st.header("Market Intelligence")

    st.write(
        "This section presents recent information, competitor-related signals, emerging technologies, "
        "and important company announcements from the collected public documents."
    )

    recent_df = load_recent_documents(limit=None)
    competitor_df = load_documents_matching_terms(COMPETITOR_TERMS, limit=None)
    competitor_table = prepare_competitor_table(competitor_df)
    technology_df = load_documents_matching_terms(TECHNOLOGY_TERMS, limit=None)
    announcement_df = load_announcements(limit=None)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Collected Updates", len(recent_df))
    col2.metric("Competitor Signals", len(competitor_table))
    col3.metric("Technology Signals", len(technology_df))
    col4.metric("Announcement Signals", len(announcement_df))

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Recent News",
            "Competitor Activities",
            "Emerging Technologies",
            "Company Announcements",
        ]
    )

    with tab1:
        st.subheader("Recent News and Collected Updates")

        if recent_df.empty:
            st.warning("No recent documents found.")
        else:
            recent_table = prepare_market_table(recent_df, "Recent News Title")

            st.dataframe(
                recent_table.reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )

    with tab2:
        st.subheader("Competitor Activities")

        st.caption(
            "This table searches for explicit competitor names such as Oracle, Microsoft Dynamics, "
            "Salesforce, Workday, ServiceNow, Infor, Epicor, and NetSuite in the collected documents."
        )

        if competitor_table.empty:
            st.info(
                "No explicit competitor activity was found in the current repository. "
                "The system still covers market risk through external industry sources, "
                "but direct competitor-name evidence is limited."
            )
        else:
            st.dataframe(
                competitor_table.reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )

    with tab3:
        st.subheader("Emerging Technologies")

        st.caption(
            "This table surfaces technology-related signals such as Business AI, Joule, SAP BTP, "
            "Cloud ERP, AI agents, and autonomous enterprise."
        )

        if technology_df.empty:
            st.warning("No emerging technology documents found.")
        else:
            technology_table = prepare_market_table(
                technology_df,
                "Emerging Technology Signal",
            )

            st.dataframe(
                technology_table.reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )

    with tab4:
        st.subheader("Important Company Announcements")

        if announcement_df.empty:
            st.warning("No company announcement documents found.")
        else:
            announcement_table = prepare_market_table(
                announcement_df,
                "Announcement Title",
            )

            st.dataframe(
                announcement_table.reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )