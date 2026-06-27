from src.dashboard.dashboard_utils import *


def show_strategic_recommendations():
    st.header("Strategic Recommendations")

    st.markdown(
        """
        <div class="section-note">
        This section retrieves strategic evidence from the knowledge base and uses the local Qwen3:8B model
        to generate CEO-level recommendations with evidence, expected impact, risk, priority, and confidence.
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Ask a strategic CEO-level question",
        value="",
        placeholder="Example: What strategic action should SAP prioritize next and why?",
        height=120,
    )

    run_button = st.button(
        "Generate Strategic Recommendations",
        type="primary",
        use_container_width=False,
    )

    if run_button:
        if not question.strip():
            st.warning("Please enter a strategic question.")
            return

        with st.spinner("Retrieving evidence and generating strategic recommendations..."):
            result = generate_ceo_answer(question)

        answer_text = result.get("answer", "")
        evidence_df = build_evidence_dataframe(result)

        st.markdown("### AI CEO Strategic Recommendations")

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

        st.markdown("### Supporting Evidence")

        if evidence_df.empty:
            st.warning("No supporting evidence was returned.")
        else:
            st.dataframe(
                evidence_df,
                use_container_width=True,
                height=320,
            )

        show_evidence_preview(result)