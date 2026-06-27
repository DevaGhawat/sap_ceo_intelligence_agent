from src.dashboard.dashboard_utils import *


def show_ceo_briefing():
    st.header("CEO Briefing")

    st.markdown(
        """
        <div class="section-note">
        This section creates an executive briefing using retrieved evidence from the knowledge base.
        The answer should explain what happened, why it matters, and what management should do next.
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "CEO briefing question",
        value="",
        placeholder="Example: What are the most important recent strategic signals for SAP?",
        height=120,
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

        answer_text = result.get("answer", "")
        evidence_df = build_evidence_dataframe(result)

        st.markdown("### Executive Briefing")

        with st.container(border=True):
            st.markdown(answer_text)

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

        st.markdown("### Briefing Evidence")

        if evidence_df.empty:
            st.warning("No supporting evidence was returned.")
        else:
            st.dataframe(
                evidence_df,
                use_container_width=True,
                height=320,
            )

        st.info(
            "The briefing is generated from retrieved evidence chunks. "
            "The final answer should connect opportunity, risk, trend, and evidence before giving a CEO-level recommendation."
        )

        show_evidence_preview(result)