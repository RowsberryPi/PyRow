"""
tests.PyRow.Concept2.Exception.BadStateException
"""
from unittest import TestCase

from pyrow.exceptions import BadStateException
from tests.mocks.device import PM3


class BadStateExceptionTests(TestCase):
    """
    Tests for BadStateException
    """

    def setUp(self):
        """
        :return:
        """
        self.device = PM3()
        self.bad_state_exception = BadStateException(self.device, "")

    def test_get_device(self):
        """
        :return:
        """
        self.assertEqual(
            self.bad_state_exception.get_device(),
            self.device
        )
