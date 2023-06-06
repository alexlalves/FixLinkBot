import logging
import os
import re
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
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

class HealthcheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print('Healthcheck OK')
        self.send_response(200)

def add_praw_logging():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

def filter_link_text_urls(comment_body: str):
    return re.sub(r'\[(.*?)\]\((.*?)\)', r'\g<2>', comment_body)

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
        filtered_body = filter_link_text_urls(comment.body)

        urls = [
            url for url in
                extractor.find_urls(
                    text = filtered_body,
                    only_unique = True,
                )
            if isinstance(url, str)
                and is_broken_url(url)
        ]

        if urls:
            comment.refresh()
            if not has_replied_to_broken_url_comment(comment.replies):
                reply_to_comment(comment, urls)

def mention_listener(reddit: praw.Reddit):
    extractor = URLExtract()

    for mention in reddit.inbox.stream():
        parent_comment = mention.parent()
        parent_comment.refresh()

        filtered_body = filter_link_text_urls(parent_comment.body)

        urls = [
            url for url in
                extractor.find_urls(
                    text = filtered_body,
                    only_unique = True,
                )
            if isinstance(url, str)
                and is_broken_url(url)
        ]

        if urls and not has_replied_to_broken_url_comment(parent_comment.replies):
            reply_to_comment(mention, urls)

        reddit.inbox.mark_read([mention])

def main():
    load_dotenv()

    if os.environ['LOGGING'] == 'TRUE':
        add_praw_logging()

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

    HTTPServer(
        ('', int(os.environ['SERVER_PORT'])),
        HealthcheckServer,
    ).serve_forever() # type: ignore

if __name__ == '__main__':
    main()
