import os
import unittest

from types import SimpleNamespace
from typing import List, Tuple
from unittest import mock

import app

class AppTestCase(unittest.TestCase):
    def test_is_broken_url(self):
        broken_url_test_cases: List[Tuple[str, bool]] = [
            # _
            ('https://en.wikipedia.org/wiki/Snake\\_case', True),
            ('https://en.wikipedia.org/wiki/Snake_case', False),

            # *
            ('https://en.wikipedia.org/wiki/\\*_(disambiguation)', True),
            ('https://en.wikipedia.org/wiki/*_(disambiguation)', False),

            # ~
            ('https://en.wikipedia.org/wiki/\\~_(album)', True),
            ('https://en.wikipedia.org/wiki/~_(album)', False),
        ]

        for test_case in broken_url_test_cases:
            assert app.is_broken_url(test_case[0]) == test_case[1]

    def test_filter_link_text_urls(self):
        filter_link_test_cases: List[Tuple[str, str]] = [
            # Normal url
            (
                'https://en.wikipedia.org/wiki/Snake_case',
                'https://en.wikipedia.org/wiki/Snake_case',
            ),

            # Broken url
            (
                'https://en.wikipedia.org/wiki/Snake\\_case',
                'https://en.wikipedia.org/wiki/Snake\\_case',
            ),

            # Broken link text, normal url
            (
                '[https://en.wikipedia.org/wiki/Snake\\_case](https://en.wikipedia.org/wiki/Snake_case)',
                'https://en.wikipedia.org/wiki/Snake_case',
            ),

            # Normal link text, broken url
            (
                '[https://en.wikipedia.org/wiki/Snake_case](https://en.wikipedia.org/wiki/Snake\\_case)',
                'https://en.wikipedia.org/wiki/Snake\\_case',
            ),

            # Broken link text, broken url
            (
                '[https://en.wikipedia.org/wiki/Snake\\_case](https://en.wikipedia.org/wiki/Snake\\_case)',
                'https://en.wikipedia.org/wiki/Snake\\_case',
            ),
        ]

        for test_case in filter_link_test_cases:
            assert app.filter_link_text_urls(test_case[0]) == test_case[1]

    def test_fix_broken_url(self):
        broken_url_test_cases: List[Tuple[str, str]] = [
            # _
            (
                'https://en.wikipedia.org/wiki/Snake\\_case',
                'https://en.wikipedia.org/wiki/Snake_case',
            ),
            (
                'https://en.wikipedia.org/wiki/Snake_case',
                'https://en.wikipedia.org/wiki/Snake_case',
            ),

            # *
            (
                'https://en.wikipedia.org/wiki/\\*_(disambiguation)',
                'https://en.wikipedia.org/wiki/*_(disambiguation)'
            ),
            (
                'https://en.wikipedia.org/wiki/*_(disambiguation)',
                'https://en.wikipedia.org/wiki/*_(disambiguation)',
            ),

            # ~
            (
                'https://en.wikipedia.org/wiki/\\~_(album)',
                'https://en.wikipedia.org/wiki/~_(album)',
            ),
            (
                'https://en.wikipedia.org/wiki/~_(album)',
                'https://en.wikipedia.org/wiki/~_(album)',
            ),
        ]

        for test_case in broken_url_test_cases:
            assert app.fix_broken_url(test_case[0]) == test_case[1]

    @mock.patch.dict(os.environ, {"USERNAME": "TEST_BOT"})
    def test_should_reply_to_broken_url_comment(self):
        mock_replies_test_cases: List[Tuple[List[SimpleNamespace], bool]] = [
            ([], True),
            ([
                SimpleNamespace(**{ 'author': 'REAL_HUMAN_BEEP_BOOP' })
            ], True),
            ([
                SimpleNamespace(**{ 'author': 'TEST_BOT' })
            ], False),
            ([
                SimpleNamespace(**{ 'author': 'REAL_HUMAN_BEEP_BOOP' }),
                SimpleNamespace(**{ 'author': 'TEST_BOT' }),
            ], False),
        ]

        for test_case in mock_replies_test_cases:
            assert app.should_reply_to_broken_url_comment(test_case[0]) == test_case[1]

if __name__ == '__main__':
    unittest.main()
