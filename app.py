import os

import praw

from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id = os.environ['CLIENT_ID'],
    client_secret = os.environ['CLIENT_SECRET'],
    password = os.environ['PASSWORD'],
    user_agent = os.environ['USER_AGENT'],
    username = os.environ['USERNAME'],
)

for submission in reddit.subreddit("test").hot(limit = 10):
    print(submission.title)

subreddit = reddit.subreddit("test")
for comment in subreddit.stream.comments(skip_existing = False):
    print(comment.body)
    # print(dir(comment))
