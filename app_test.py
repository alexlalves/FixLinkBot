import unittest

from typing import List, Tuple

import app

class AppTestCase(unittest.TestCase):
    def test_is_broken_url(self):
        broken_url_test_cases: List[Tuple[str, bool]] = [
            # _
            ('https://en.wikipedia.org/wiki/~\\_(album)', True),
            ('https://en.wikipedia.org/wiki/~_(album)', False),

            # ~
            ('https://en.wikipedia.org/wiki/\\~_(album)', True),
            ('https://en.wikipedia.org/wiki/~_(album)', False),

            # *
            ('https://en.wikipedia.org/wiki/\\*_(disambiguation)', True),
            ('https://en.wikipedia.org/wiki/*_(disambiguation)', False),
        ]

        for test_case in broken_url_test_cases:
            assert app.is_broken_url(test_case[0]) == test_case[1]

if __name__ == '__main__':
    unittest.main()
