import logging
import os
import re
import threading

from string import Template
from typing import Any, List, Union

import praw

from dotenv import load_dotenv
from urlextract import URLExtract

MESSAGE_TEMPLATE = Template(
"""Hi, I noticed that some of your links might be broken for some reddit users.
Here is my best attempt at fixing them:

$fixed_links

I am a bot, beep boop.
If you have any issues with me, please contact u/Magmagan.
"""
)

def add_logging():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

def is_broken_url(url: Union[str, Any]) -> bool:
    if isinstance(url, str):
        return (
            url.find('\\_') != -1
            or url.find('%5C') != -1
            or url.find('))') != -1
        )
    raise TypeError(f'Expected {url} to be of type str')

def fix_broken_urls(urls: List[str]) -> List[str]:
    return [
        re.sub(r'(\\_)|(%5[cC]_)', '_', url)
        for url in urls
    ]

def has_replied_to_broken_url_comment(replies):
    return any(
        comment.author == os.environ['USERNAME']
        for comment in replies
    )

def message(urls: List[str]):
    return MESSAGE_TEMPLATE.substitute({
        'fixed_links': "\n\n".join(urls)
    })

def reply_to_comment(comment, broken_urls: List[str]):
    comment.reply(
        message(
            fix_broken_urls(broken_urls)
        )
    )

def comment_listener(reddit: praw.Reddit):
    extractor = URLExtract()

    subreddit = reddit.subreddit('test')
    for comment in subreddit.stream.comments(skip_existing = True):
        urls = extractor.find_urls(
            text = comment.body,
            only_unique = True,
        )

        broken_urls = [
            url for url in urls
            if is_broken_url(url) and isinstance(url, str)
        ]

        if broken_urls:
            comment.refresh()
            if not has_replied_to_broken_url_comment(comment.replies):
                reply_to_comment(comment, broken_urls)

def mention_listener(reddit: praw.Reddit):
    extractor = URLExtract()

    for mention in reddit.inbox.stream():
        parent_comment = mention.parent()
        parent_comment.refresh()

        urls = extractor.find_urls(
            text = parent_comment.body,
            only_unique = True,
        )

        print(urls)

        broken_urls = [
            url for url in urls
            if is_broken_url(url) and isinstance(url, str)
        ]

        print(broken_urls)

        if broken_urls:
            print(has_replied_to_broken_url_comment(parent_comment.replies))
            if not has_replied_to_broken_url_comment(parent_comment.replies):
                reply_to_comment(mention, broken_urls)

        reddit.inbox.mark_read([mention])

def main():
    load_dotenv()

    if os.environ['LOGGING'] == 'True':
        add_logging()

    reddit = praw.Reddit(
        client_id = os.environ['CLIENT_ID'],
        client_secret = os.environ['CLIENT_SECRET'],
        password = os.environ['PASSWORD'],
        user_agent = os.environ['USER_AGENT'],
        username = os.environ['USERNAME'],
    )

    threading.Thread(
        target = comment_listener,
        args = (reddit,)
    ).start()

    threading.Thread(
        target=mention_listener,
        args=(reddit,)
    ).start()


if __name__ == '__main__':
    main()
