"""
tests.PyRow.Concept2.CsafeCmd
"""
import logging
from unittest.mock import MagicMock


class CsafeCmd(MagicMock):
    def __init__(self):
        """
        :return:
        """
        MagicMock.__init__(self)

        self.read_call_count = 0

        self.__responses = []

    def set_responses(self, responses):
        """
        :param [] responses:
        :return:
        """
        self.__responses = responses
        self.read_call_count = 0

    def read(self, transmission):
        """
        :param transmission:
        :return []:
        """
        if self.read_call_count >= len(self.__responses):
            raise Exception("Not enough mocked responses")
        response = self.__responses[self.read_call_count]
        self.read_call_count += 1
        logging.debug("Read: %s", response)
        return response

    def write(self, commands):
        """
        :param commands:
        :return:
        """
        logging.debug("Write: %s", commands)
        return []
