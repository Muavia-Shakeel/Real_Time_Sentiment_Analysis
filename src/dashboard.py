import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from sqlalchemy.orm import Session
from database import SessionLocal
from models import RedditPost
from trend_forecasting import forecast_trend
from integration import process_and_store_posts

def get_all_posts():
    """Retrieve all Reddit posts from the database."""
    db = SessionLocal()
    try:
        posts = db.query(RedditPost).order_by(RedditPost.created_utc.desc()).all()
        return posts
    finally:
        db.close()

def posts_to_dataframe(posts):
    """Convert a list of RedditPost objects into a pandas DataFrame."""
    data = []
    for post in posts:
        data.append({
            "ID": post.id,
            "Title": post.title,
            "Content": post.content,
            "Created UTC": post.created_utc,
            "Sentiment": post.sentiment_label,
            "Score": post.sentiment_score,
        })
    df = pd.DataFrame(data)
    df["Created UTC"] = pd.to_datetime(df["Created UTC"])
    return df

def filter_posts(df, sentiments, start_date, end_date):
    """Filter DataFrame based on selected sentiments and date range."""
    mask = (df["Created UTC"].dt.date >= start_date) & (df["Created UTC"].dt.date <= end_date)
    df = df.loc[mask]
    if sentiments:
        df = df[df["Sentiment"].isin(sentiments)]
    return df

def aggregate_data(df, freq='1h'):
    """Aggregate sentiment scores into time buckets."""
    df = df.copy()
    df.set_index("Created UTC", inplace=True)
    aggregated = df.resample(freq)["Score"].mean().reset_index()
    return aggregated

# Page Layout
st.set_page_config(
    page_title="Real-Time Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Filters
st.sidebar.header("Filters & Settings")

# Button to fetch new posts
if st.sidebar.button("Fetch New Posts"):
    process_and_store_posts(subreddit='worldnews', limit=5)
    st.sidebar.success("Fetched new posts and updated the database!")

sentiment_options = st.sidebar.multiselect(
    "Select Sentiment Types",
    options=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    default=["POSITIVE", "NEGATIVE", "NEUTRAL"]
)

today = datetime.date.today()
default_start = today - datetime.timedelta(days=7)
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", today)

freq_option = st.sidebar.selectbox(
    "Aggregation Frequency",
    options=["1h", "6h", "12h", "1d"],
    index=0,
    help="Choose the time interval for aggregating sentiment scores."
)

# Data Retrieval and Processing
all_posts = get_all_posts()
if all_posts:
    posts_df = posts_to_dataframe(all_posts)
    filtered_df = filter_posts(posts_df, sentiment_options, start_date, end_date)
else:
    filtered_df = pd.DataFrame()

# Main Dashboard Layout
st.markdown(
    """
    <div style='background-color: #282C34; padding: 10px; border-radius: 8px;'>
    <h1 style='color: white; text-align: center;'>🌍 Real-Time Sentiment Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("### Recent Reddit Posts")
if not filtered_df.empty:
    st.dataframe(filtered_df.sort_values("Created UTC", ascending=False))
else:
    st.write("No posts available for the selected filters.")

st.write("### Sentiment Trend Over Time")
if not filtered_df.empty:
    aggregated = aggregate_data(filtered_df, freq=freq_option)
    fig = px.line(
        aggregated,
        x="Created UTC",
        y="Score",
        title="Sentiment Score Over Time",
        labels={"Score": "Average Sentiment Score", "Created UTC": "Time"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No data to display for the selected filters.")

# Forecasting
if st.sidebar.button("Generate Forecast"):
    if not filtered_df.empty:
        try:
            aggregated_hist = aggregate_data(filtered_df, freq=freq_option)
            aggregated_hist.rename(columns={"Created UTC": "ds", "Score": "y"}, inplace=True)

            forecast_df = forecast_trend(aggregated_hist, periods=5, freq=freq_option)

            combined = aggregated_hist.copy()
            combined["Type"] = "Historical"
            fc_plot = forecast_df[["ds", "yhat"]].rename(columns={"ds": "Created UTC", "yhat": "Score"})
            fc_plot["Type"] = "Forecast"
            combined = pd.concat([combined, fc_plot], ignore_index=True)

            fig_forecast = px.line(
                combined,
                x="Created UTC",
                y="Score",
                color="Type",
                title="Historical vs Forecasted Sentiment",
                labels={"Score": "Sentiment Score", "Created UTC": "Time"}
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
        except Exception as e:
            st.error(f"Forecast generation failed: {e}")
    else:
        st.write("No sufficient data to generate a forecast. Please adjust your filters.")

# Sentiment Distribution
st.write("### Sentiment Distribution")
if not filtered_df.empty:
    sentiment_counts = filtered_df["Sentiment"].value_counts()
    fig_pie = px.pie(
        sentiment_counts,
        values=sentiment_counts,
        names=sentiment_counts.index,
        title="Distribution of Sentiment Types",
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.write("No data available to display sentiment distribution.")

# Downloadable Data
if not filtered_df.empty:
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    csv = convert_df(filtered_df)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv",
    )
