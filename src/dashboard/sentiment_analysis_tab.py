from src.dashboard.dashboard_utils import *


def show_sentiment_analysis():
    st.header("Sentiment Analysis")


    st.markdown(
    """
    <div class="section-note">
    Sentiment shown here represents the tone of collected articles and public business signals.
    It does not represent direct social media sentiment.
    </div>
    """,
    unsafe_allow_html=True,
    )
    
    st.write(
        "This section applies VADER sentiment analysis to collected document text. "
        "It includes news/content sentiment, public-signal sentiment, and sentiment trends. "
        "Because the dataset mainly contains articles and official/public web sources, this is interpreted as content tone, not direct survey opinion."
    )

    sentiment_df = build_sentiment_dataframe()

    if sentiment_df.empty:
        st.warning("No documents available for sentiment analysis.")
        return

    if "sentiment_date" not in sentiment_df.columns:
        if "published_date" in sentiment_df.columns:
            published_series = pd.to_datetime(
                sentiment_df["published_date"],
                errors="coerce",
                utc=True,
            )
        else:
            published_series = pd.Series(pd.NaT, index=sentiment_df.index)

        if "collected_at" in sentiment_df.columns:
            collected_series = pd.to_datetime(
                sentiment_df["collected_at"],
                errors="coerce",
                utc=True,
            )
        else:
            collected_series = pd.Series(pd.NaT, index=sentiment_df.index)

        final_date_series = published_series.fillna(collected_series)
        sentiment_df["sentiment_date"] = final_date_series.dt.date

        date_sources = []

        for published_value, collected_value in zip(published_series, collected_series):
            if not pd.isna(published_value):
                date_sources.append("published_date")
            elif not pd.isna(collected_value):
                date_sources.append("collected_at")
            else:
                date_sources.append("not_available")

        sentiment_df["date_source"] = date_sources

    sentiment_counts = (
        sentiment_df["sentiment_label"]
        .value_counts()
        .reset_index()
    )

    sentiment_counts.columns = ["Sentiment Label", "Document Count"]

    positive_count = int((sentiment_df["sentiment_label"] == "positive").sum())
    neutral_count = int((sentiment_df["sentiment_label"] == "neutral").sum())
    negative_count = int((sentiment_df["sentiment_label"] == "negative").sum())

    news_df = sentiment_df[
        sentiment_df["source_type"].isin(["external_news", "financial", "news"])
    ]

    public_signal_df = sentiment_df[
        sentiment_df["source_type"].isin(["external_news", "community", "news"])
    ]

    avg_news_sentiment = 0
    avg_public_signal = 0

    if not news_df.empty:
        avg_news_sentiment = round(float(news_df["sentiment_score"].mean()), 4)

    if not public_signal_df.empty:
        avg_public_signal = round(float(public_signal_df["sentiment_score"].mean()), 4)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Positive", positive_count)
    col2.metric("Neutral", neutral_count)
    col3.metric("Negative", negative_count)
    col4.metric("News Sentiment Avg", avg_news_sentiment)
    col5.metric("Public Signal Avg", avg_public_signal)

    fig = px.bar(
        sentiment_counts,
        x="Sentiment Label",
        y="Document Count",
        text="Document Count",
        title="Document Sentiment Distribution",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sentiment Trends")

    st.caption(
        "The trend is based on the document published date when available. "
        "If the published date is missing, the system falls back to the collection date. "
        "The chart groups sentiment by month to make the trend easier to read."
    )

    valid_date_df = sentiment_df.dropna(subset=["sentiment_date"])

    if not valid_date_df.empty:
        date_source_df = (
            valid_date_df["date_source"]
            .value_counts()
            .reset_index()
        )

        date_source_df.columns = ["Date Source", "Document Count"]

        with st.expander("Date source used for sentiment trend"):
            st.write(
                "This confirms whether the trend uses article published dates or fallback collection dates."
            )
            st.dataframe(date_source_df, use_container_width=True)

        valid_date_df = valid_date_df.copy()

        valid_date_df["sentiment_month"] = pd.to_datetime(
            valid_date_df["sentiment_date"],
            errors="coerce",
        ).dt.to_period("M").astype(str)

        trend_df = (
            valid_date_df
            .groupby(["sentiment_month", "sentiment_label"])
            .size()
            .reset_index(name="document_count")
        )

        fig = px.line(
            trend_df,
            x="sentiment_month",
            y="document_count",
            color="sentiment_label",
            markers=True,
            title="Monthly Sentiment Trend by Published Date",
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        topic_sentiment_df = (
            sentiment_df
            .groupby(["topic", "sentiment_label"])
            .size()
            .reset_index(name="document_count")
        )

        fig = px.bar(
            topic_sentiment_df,
            x="topic",
            y="document_count",
            color="sentiment_label",
            title="Sentiment Distribution by Topic",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("News and Public Signal Sentiment")

    news_columns = [
        "title",
        "source_name",
        "source_type",
        "topic",
        "published_date",
        "sentiment_date",
        "date_source",
        "sentiment_score",
        "sentiment_label",
        "url",
    ]

    available_news_columns = [
        column for column in news_columns
        if column in sentiment_df.columns
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.write("News / External / Financial Sentiment")

        if news_df.empty:
            st.info("No news-like source documents available.")
        else:
            st.dataframe(
                news_df[available_news_columns].sort_values(
                    by="sentiment_score",
                    ascending=False,
                ),
                use_container_width=True,
            )

    with col2:
        st.write("Public Signal Sentiment")

        if public_signal_df.empty:
            st.info("No public-signal source documents available.")
        else:
            st.dataframe(
                public_signal_df[available_news_columns].sort_values(
                    by="sentiment_score",
                    ascending=False,
                ),
                use_container_width=True,
            )

    st.subheader("All Sentiment Details")

    display_columns = [
        "title",
        "source_name",
        "source_type",
        "topic",
        "published_date",
        "sentiment_date",
        "date_source",
        "sentiment_score",
        "sentiment_label",
        "quality_score",
        "url",
    ]

    available_display_columns = [
        column for column in display_columns
        if column in sentiment_df.columns
    ]

    display_df = sentiment_df[available_display_columns].sort_values(
        by="sentiment_score",
        ascending=False,
    )

    st.dataframe(display_df, use_container_width=True)

