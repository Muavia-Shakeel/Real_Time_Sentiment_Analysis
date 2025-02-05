# src/data_ingestion.py

import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from preprocessing import clean

def reddit_instance():
    """
    Initializes and returns a Reddit instance using PRAW.
    """
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    return reddit

def fetch_new_posts(subreddit_name='worldnews', limit=10):
    """
    Fetches the latest posts from a given subreddit.
    
    Parameters:
        subreddit_name (str): Name of the subreddit to fetch posts from.
        limit (int): Number of posts to fetch.
        
    Returns:
        posts (list of dict): List of dictionaries containing post title and content.
    """
    reddit = reddit_instance()
    # Correct: Get the subreddit object first, then call .new() on it
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    
    for post in subreddit.new(limit=limit):
        posts.append({
            'title': clean(post.title),
            'content': clean(post.selftext),
            'created_utc': post.created_utc
        })
    
    return posts

if __name__ == '__main__':
    # For testing purposes: fetch and print the 5 newest posts from r/worldnews
    posts = fetch_new_posts(subreddit_name='worldnews', limit=5)
    for post in posts:
        print("Title:", post['title'])
        print("Content:", post['content'])
        print("-" * 50)
