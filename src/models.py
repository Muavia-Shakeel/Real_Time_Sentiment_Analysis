# src/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class RedditPost(Base):
    __tablename__ = "reddit_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    created_utc = Column(DateTime, default=datetime.datetime.utcnow)
    sentiment_label = Column(String, nullable=False)
    sentiment_score = Column(Float, nullable=False)

    def __repr__(self):
        return f"<RedditPost(id={self.id}, title={self.title}, sentiment={self.sentiment_label}, score={self.sentiment_score})>"
