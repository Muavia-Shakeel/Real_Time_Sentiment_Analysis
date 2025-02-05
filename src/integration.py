# src/integration.py

import datetime
from data_ingestion import fetch_new_posts
from sentiment_analysis import analyze_sentiment
from database import SessionLocal
from crud import create_reddit_post

# We'll also reuse our sentiment conversion utility.
def sentiment_to_numeric(sentiment):
    """
    Convert sentiment output to a numeric value.
    Returns a positive score for 'POSITIVE', negative for 'NEGATIVE', or 0 otherwise.
    """
    label = sentiment.get('label', 'NEUTRAL').upper()
    score = sentiment.get('score', 0.0)
    if label == 'POSITIVE':
        return score
    elif label == 'NEGATIVE':
        return -score
    else:
        return 0.0

def process_and_store_posts(subreddit='worldnews', limit=5):
    """
    Fetch posts from a subreddit, analyze their sentiment,
    and store the results in the database.
    """
    posts = fetch_new_posts(subreddit_name=subreddit, limit=limit)
    db = SessionLocal()  # Create a database session
    try:
        for idx, post in enumerate(posts, start=1):
            # Combine title and content for a full context
            text = f"{post['title']} {post['content']}".strip()
            sentiment = analyze_sentiment(text)
            numeric_sentiment = sentiment_to_numeric(sentiment)
            
            # Convert the UNIX timestamp to a datetime object (UTC)
            created_dt = datetime.datetime.fromtimestamp(post['created_utc'])
            
            # Store the post in the database
            stored_post = create_reddit_post(
                db=db,
                title=post['title'],
                content=post['content'],
                created_utc=created_dt,
                sentiment_label=sentiment['label'],
                sentiment_score=numeric_sentiment
            )
            print(f"Stored Post #{idx}: {stored_post}")
    finally:
        db.close()

if __name__ == '__main__':
    process_and_store_posts(subreddit='worldnews', limit=5)
