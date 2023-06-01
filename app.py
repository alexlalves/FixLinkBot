import os
import re

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

def is_broken_url(url: Union[str, Any]) -> bool:
    if isinstance(url, str):
        return (
            url.find('\\_') != -1 \
            or url.find('%5C') != -1
        )
    raise TypeError(f'Expected {url} to be of type str')

def fix_broken_urls(urls: List[str]) -> List[str]:
    return [
        re.sub(r'(\\_)|(%5[cC]_)', '_', url)
        for url in urls
    ]

def has_replied_to_broken_url_comment(replies):
    for comment in replies:
        print(comment.author)
        if comment.author == os.environ['USERNAME']:
            return True
    return False

def message(urls: List[str]):
    print(MESSAGE_TEMPLATE.substitute({
        'fixed_links': "\n\n".join(urls)
    }))

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

        broken_urls = [
            url for url in urls
            if is_broken_url(url) and isinstance(url, str)
        ]

        if broken_urls:
            comment.refresh()
            if not has_replied_to_broken_url_comment(comment.replies):
                new_urls = fix_broken_urls(broken_urls)
                message(new_urls)

if __name__ == '__main__':
    main()
