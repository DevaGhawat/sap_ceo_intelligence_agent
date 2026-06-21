from src.dashboard.dashboard_utils import *


def show_opportunity_monitor():
    st.header("Opportunity Monitor")

    st.write(
        "This section shows opportunity-related documents and converts them into opportunity titles, "
        "impact levels, evidence snippets, and confidence scores."
    )

    total_opportunities = count_documents_by_topic("opportunity")
    avg_quality = get_average_quality_by_topic("opportunity")
    opportunity_df = load_documents_by_topic("opportunity", limit=None)
    opportunity_table = prepare_opportunity_table(opportunity_df)

    col1, col2, col3 = st.columns(3)

    col1.metric("Opportunity Documents", total_opportunities)
    col2.metric("Average Confidence", avg_quality)
    col3.metric("Displayed Opportunities", len(opportunity_table))

    if opportunity_table.empty:
        st.warning("No opportunity documents found.")
        return

    impact_counts = (
        opportunity_table["Impact Level"]
        .value_counts()
        .reset_index()
    )
    impact_counts.columns = ["Impact Level", "Count"]

    fig = px.bar(
        impact_counts,
        x="Impact Level",
        y="Count",
        text="Count",
        title="Opportunity Impact Levels",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Opportunity Table")
    st.dataframe(
    opportunity_table.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    )

    st.subheader("Opportunity Evidence Preview")

    for _, row in opportunity_df.head(8).iterrows():
        with st.expander(row["title"]):
            st.write(row["preview"])
            st.write("Source:", row["source_name"])
            st.write("URL:", row["url"])

