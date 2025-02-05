# src/trend_forecasting.py

import pandas as pd
import datetime
from prophet import Prophet

# Import our existing modules
from data_ingestion import fetch_new_posts
from sentiment_analysis import analyze_sentiment

def sentiment_to_numeric(sentiment):
    """
    Convert sentiment analysis output to a numeric value.
    
    Parameters:
        sentiment (dict): The sentiment dictionary with 'label' and 'score'.
        
    Returns:
        float: A numeric sentiment score.
               Positive sentiment returns a positive score,
               Negative sentiment returns a negative score,
               Neutral returns 0.
    """
    label = sentiment.get('label', 'NEUTRAL').upper()
    score = sentiment.get('score', 0.0)
    if label == 'POSITIVE':
        return score
    elif label == 'NEGATIVE':
        return -score
    else:
        return 0.0

def create_sentiment_timeseries(subreddit='worldnews', limit=50):
    """
    Fetch posts from a subreddit, analyze their sentiment,
    and create a time series DataFrame with sentiment scores.
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'ds' (datetime) and 'score' (numeric sentiment score).
    """
    posts = fetch_new_posts(subreddit_name=subreddit, limit=limit)
    records = []
    
    for post in posts:
        # Combine title and content for a fuller context
        text = f"{post['title']} {post['content']}".strip()
        sentiment = analyze_sentiment(text)
        numeric_sentiment = sentiment_to_numeric(sentiment)
        
        # Convert the UNIX timestamp to a datetime object (UTC)
        dt = datetime.datetime.utcfromtimestamp(post['created_utc'])
        records.append({'ds': dt, 'score': numeric_sentiment})
    
    df = pd.DataFrame(records)
    df.sort_values('ds', inplace=True)
    return df

def aggregate_timeseries(df, freq='1H'):
    """
    Aggregate the sentiment time series data into specified time buckets.
    
    Parameters:
        df (pd.DataFrame): DataFrame with 'ds' and 'score'.
        freq (str): Resampling frequency (e.g., '1H' for hourly).
    
    Returns:
        pd.DataFrame: Aggregated DataFrame.
    """
    # Set the datetime column as the index
    df.set_index('ds', inplace=True)
    # Resample the data by taking the mean of sentiment scores within each interval
    aggregated = df.resample(freq).mean().reset_index()
    return aggregated

def forecast_trend(aggregated_df, periods=5, freq='H'):
    """
    Fit a Prophet model to the aggregated data and forecast future sentiment.
    
    Parameters:
        aggregated_df (pd.DataFrame): Aggregated DataFrame with 'ds' and 'score'.
        periods (int): Number of future time periods to forecast.
        freq (str): Frequency of forecast periods (e.g., 'H' for hourly).
        
    Returns:
        pd.DataFrame: Forecasted DataFrame with 'ds', 'yhat', 'yhat_lower', and 'yhat_upper'.
    """
    model = Prophet()
    model.fit(aggregated_df)
    
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    return forecast

if __name__ == '__main__':
    # Step 1: Create the time series from recent Reddit posts
    df = create_sentiment_timeseries(subreddit='worldnews', limit=50)
    print("Raw Time Series Data:")
    print(df)
    
    # Step 2: Aggregate data into hourly buckets (adjust frequency as needed)
    aggregated_df = aggregate_timeseries(df, freq='1H')
    print("\nAggregated Time Series Data:")
    print(aggregated_df)
    
    # Step 3: Forecast future sentiment trend for the next 5 hours
    forecast = forecast_trend(aggregated_df, periods=5, freq='H')
    print("\nForecast:")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
