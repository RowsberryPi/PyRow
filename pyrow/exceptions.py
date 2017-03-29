class BadStateException(Exception):
    """
    BadStateException
    """

    def __init__(self, device, state):
        """
        :param PerformanceMonitor device:
        :param string state:
        :return:
        """
        super(BadStateException, self).__init__(device, state)
        self.__device = device
        self.__state = state

    def get_device(self):
        """
        :return PerformanceMonitor:
        """
        return self.__device

    def __str__(self):
        """
        :return string:
        """
        return "{0} has state: {1}".format(self.__device.get_serial_number(), self.__state)


class RetryLimitException(Exception):
    """
    RetryLimitException
    """

    def __init__(self, waiting_for):
        """
        :param string waiting_for:
        :return:
        """
        self.__waiting_for = waiting_for

    def __str__(self):
        """
        :return string:
        """
        return "Retry limit reached, waiting for {0}".format(self.__waiting_for)
