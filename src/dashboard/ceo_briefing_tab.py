from src.dashboard.dashboard_utils import *
from src.agent.ceo_agent import run_ceo_agent


def show_ceo_briefing():
    st.header("CEO Briefing")

    st.markdown(
        """
        <div class="section-note">
        This section uses the CEO Agent to create an executive briefing.
        The agent plans the task, selects tools, retrieves evidence, analyzes signals,
        validates the recommendation, and saves the run in memory.
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

        with st.spinner("Running CEO agent: planning, retrieving, analyzing, validating..."):
            result = run_ceo_agent(question)

        answer_text = result.get("answer", "")
        evidence_df = build_evidence_dataframe(result)

        st.markdown("### Executive Briefing")

        with st.container(border=True):
            st.markdown(answer_text)

        st.markdown("### Agent Execution Trace")

        execution_trace = result.get("execution_trace", [])

        if execution_trace:
            for item in execution_trace:
                step = item.get("step", "Step")
                details = item.get("details", "")
                st.write(f"**{step}:** {details}")
        else:
            st.info("No execution trace returned.")

        st.markdown("### Agent Validation")

        validation = result.get("validation", {})

        if validation.get("passed"):
            st.success("Validation passed. Briefing is supported by retrieved evidence.")
        else:
            st.error("Validation failed. Some checks need attention.")

        checks = validation.get("checks", {})

        if checks:
            st.json(checks)

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

        show_evidence_preview(result)