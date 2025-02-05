# src/crud.py

from sqlalchemy.orm import Session
from models import RedditPost

def create_reddit_post(
    db: Session,
    title: str,
    content: str,
    created_utc,
    sentiment_label: str,
    sentiment_score: float
):
    """
    Create a new RedditPost record in the database.
    
    Parameters:
        db (Session): Database session.
        title (str): Post title.
        content (str): Post content.
        created_utc (datetime): Datetime object for when the post was created.
        sentiment_label (str): Sentiment label (e.g., 'POSITIVE', 'NEGATIVE', 'NEUTRAL').
        sentiment_score (float): Numeric sentiment score.
    
    Returns:
        RedditPost: The newly created RedditPost object.
    """
    post = RedditPost(
        title=title,
        content=content,
        created_utc=created_utc,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
