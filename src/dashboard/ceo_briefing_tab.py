from src.dashboard.dashboard_utils import *


def show_ceo_briefing():
    st.header("CEO Briefing")

    st.write(
        "This section creates an executive briefing around three CEO questions: "
        "What happened? Why does it matter? What should management do next?"
    )

    default_question = (
        "What happened recently in SAP's Business AI and cloud ERP environment, "
        "why does it matter, and what should management do next?"
    )

    question = st.text_area(
        "CEO briefing question",
        value=default_question,
        height=110,
        help="The briefing will be generated from retrieved SAP-related evidence.",
    )

    run_button = st.button(
        "Generate CEO Briefing",
        type="primary",
        use_container_width=False,
    )

    if run_button:
        if not question.strip():
            st.warning("Please enter a CEO briefing question.")
            return

        with st.spinner("Retrieving evidence and generating CEO briefing..."):
            result = generate_ceo_answer(question)

        evidence_df = build_evidence_dataframe(result)

        if not evidence_df.empty:
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric("Evidence Items", len(evidence_df))

            with metric_col2:
                if "Final Score" in evidence_df.columns:
                    avg_score = evidence_df["Final Score"].mean()
                    st.metric("Avg Retrieval Score", round(avg_score, 3))
                else:
                    st.metric("Avg Retrieval Score", "N/A")

            with metric_col3:
                if "Source Type" in evidence_df.columns:
                    source_count = evidence_df["Source Type"].nunique()
                    st.metric("Source Types", source_count)
                else:
                    st.metric("Source Types", "N/A")

        st.markdown("### What happened?")

        with st.container(border=True):
            if evidence_df.empty:
                st.write("No evidence was retrieved.")
            else:
                top_titles = evidence_df.head(3)["Title"].tolist()
                st.write(
                    "The system retrieved recent strategic signals from the knowledge repository, including: "
                    + "; ".join(top_titles)
                    + "."
                )

        st.markdown("### Why does it matter?")

        with st.container(border=True):
            st.write(
                "The retrieved evidence connects SAP's Business AI and cloud ERP strategy with customer adoption, "
                "enterprise data readiness, governance risks, and external market signals. These are important because "
                "CEO-level decisions need both opportunity and risk evidence, not only isolated news summaries."
            )

        st.markdown("### What should management do next?")

        with st.container(border=True):
            st.markdown(result["answer"])

        st.markdown("### Briefing Evidence")

        if evidence_df.empty:
            st.warning("No briefing evidence was returned.")
        else:
            st.dataframe(
                evidence_df,
                use_container_width=True,
                height=320,
            )

        show_evidence_preview(result)