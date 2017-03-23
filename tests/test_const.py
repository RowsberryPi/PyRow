import re
from unittest import TestCase

from pyrow import const


class ConstTests(TestCase):
    SEM_VER = re.compile('^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-'
                         'zA-Z-]*)(\.(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)?(\+[0-9a-zA-Z-]+(\.['
                         '0-9a-zA-Z-]+)*)?$')

    def test_semantic_version(self):
        self.assertTrue(
            self.SEM_VER.fullmatch(const.__version__)
        )
