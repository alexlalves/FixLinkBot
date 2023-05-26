import os

from typing import Any, Union

import praw

from dotenv import load_dotenv
from urlextract import URLExtract

def is_broken_url(url: Union[str, Any]) -> bool:
    if isinstance(url, str):
        return (
            url.find('\\_') != -1 \
            or url.find('%5C') != -1
        )
    raise TypeError(f'Expected {url} to be of type str')

def has_replied_to_broken_url_comment(replies):
    for comment in replies:
        print(comment.author)
        if comment.author == os.environ['USERNAME']:
            return True
    return False

def main():
    load_dotenv()

    reddit = praw.Reddit(
        client_id = os.environ['CLIENT_ID'],
        client_secret = os.environ['CLIENT_SECRET'],
        password = os.environ['PASSWORD'],
        user_agent = os.environ['USER_AGENT'],
        username = os.environ['USERNAME'],
    )

    subreddit = reddit.subreddit('test')
    for comment in subreddit.stream.comments(skip_existing = False):
        extractor = URLExtract()
        urls = extractor.find_urls(
            text = comment.body,
            only_unique = True,
        )

        broken_urls = [url for url in urls if is_broken_url(url)]

        if broken_urls:
            print(broken_urls)
            print(comment.replies)
            comment.refresh()
            print(comment.replies.list())
            print(has_replied_to_broken_url_comment(comment.replies))

if __name__ == '__main__':
    main()
