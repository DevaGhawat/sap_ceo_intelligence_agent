from src.dashboard.dashboard_utils import *


def show_risk_monitor():
    st.header("Risk Monitor")

    st.write(
        "This section shows risk-related documents and converts them into risk titles, "
        "risk categories, severity levels, evidence snippets, and confidence scores."
    )

    total_risks = count_documents_by_topic("risk")
    avg_quality = get_average_quality_by_topic("risk")
    risk_df = load_documents_by_topic("risk", limit=None)
    risk_table = prepare_risk_table(risk_df)

    col1, col2, col3 = st.columns(3)

    col1.metric("Risk Documents", total_risks)
    col2.metric("Average Confidence", avg_quality)
    col3.metric("Displayed Risks", len(risk_table))

    if risk_table.empty:
        st.warning("No risk documents found.")
        return

    severity_counts = (
        risk_table["Severity Level"]
        .value_counts()
        .reset_index()
    )
    severity_counts.columns = ["Severity Level", "Count"]

    fig = px.bar(
        severity_counts,
        x="Severity Level",
        y="Count",
        text="Count",
        title="Risk Severity Levels",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Risk Table")
    st.dataframe(
    risk_table.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    )

    st.subheader("Risk Evidence Preview")

    for _, row in risk_df.head(8).iterrows():
        with st.expander(row["title"]):
            st.write(row["preview"])
            st.write("Source:", row["source_name"])
            st.write("URL:", row["url"])

