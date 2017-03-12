"""
tests.PyRow.Concept2.Exception.BadStateException
"""
import unittest

from tests.Concept2.Device import PM3


class BadStateExceptionTests(unittest.TestCase):
    """
    Tests for BadStateException
    """

    def setUp(self):
        """
        :return:
        """
        self.device = PM3()
        # TODO Fix BadStateException tests
        # self.bad_state_exception = BadStateException(Exception)

        # def test_get_device(self):
        #     """
        #     :return:
        #     """
        #     self.assertEqual(
        #         self.bad_state_exception.get_device(),
        #         self.device
        #     )
