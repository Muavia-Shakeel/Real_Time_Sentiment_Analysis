import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

def test_reddit_credentials():
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        # Attempt to fetch the front page to see if credentials are accepted.
        for submission in reddit.front.hot(limit=3):
            print(submission.title)
        print("Credentials are working!")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    test_reddit_credentials()
