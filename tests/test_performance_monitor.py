"""
tests.PyRow.Concept2.PerformanceMonitorTests
"""
import sys
from unittest import TestCase
from unittest.mock import MagicMock

from freezegun import freeze_time

from tests.mocks.csafe_cmd import CsafeCmd
from tests.mocks.device import PM3

sys.modules['usb'] = MagicMock()
sys.modules['usb.util'] = MagicMock()
sys.modules['pyrow.csafe.cmd'] = MagicMock()  # MagicMocking the file
sys.modules['pyrow.csafe.cmd'].CsafeCmd = CsafeCmd()


def usb_util_get_string_side_effect(device, key):
    """
    :param device:
    :param key:
    :return:
    """
    return device.get_usb_util_string(key)


sys.modules['usb'].util.get_string = MagicMock(side_effect=usb_util_get_string_side_effect)
sys.modules['usb'].core.find = MagicMock(return_value=[PM3()])

sys.modules['Lock'] = MagicMock()
sys.modules['Lock'].acquire = MagicMock()

from pyrow.exceptions import BadStateException, RetryLimitException  # noqa E402
from pyrow.performance_monitor import PerformanceMonitor  # noqa E402
from pyrow.response import Response  # noqa E402

class PerformanceMonitorTests(TestCase):
    """
    Tests for PerformanceMonitor
    """

    def setUp(self):
        """
        Set up the instance before each test
        :return:
        """
        self.device = PM3()
        self.reset_responses = [
            {
                'CSAFE_GETSTATUS_CMD': [1]  # Ready state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]
            },
            {
                'CSAFE_GETSTATUS_CMD': [1]
            },
            {
                'CSAFE_GETSTATUS_CMD': [1]
            }
        ]

        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses(self.reset_responses)
        self.performance_monitor = PerformanceMonitor(self.device)

    def test_find(self):
        """
        PerformanceMonitor.find - it should return currently connected performance monitors
        :return:
        """
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses(
            self.reset_responses
        )

        returned_pms = PerformanceMonitor.find()

        self.assertEqual(
            returned_pms[0].__class__,
            PerformanceMonitor
        )

    @freeze_time("2015-11-10 14:45:22")
    def test_set_clock(self):
        """
        PerformanceMonitor.set_clock - it should set the clock to the computer's time
        :return:
        """
        self.performance_monitor.send_commands = MagicMock()
        self.performance_monitor.set_clock()

        self.performance_monitor.send_commands.assert_called_with(
            ['CSAFE_SETTIME_CMD', 14, 45, 22, 'CSAFE_SETDATE_CMD', 115, 11, 10]
        )

    def test_get_manufacturer(self):
        """
        PerformanceMonitor.get_manufacturer - it should return the name of the manufacturer
        :return:
        """
        self.assertEqual(
            self.performance_monitor.get_manufacturer(),
            "Concept2"
        )

    def test_get_product(self):
        """
        PerformanceMonitor.get_product - it should the name of the product
        :return:
        """
        self.assertEqual(
            self.performance_monitor.get_product(),
            "Concept2 Performance Monitor 3 (PM3)"
        )

    def test_serial_number(self):
        """
        PerformanceMonitor.get_serial_number - it should return the serial number
        :return:
        """
        self.assertEqual(
            self.performance_monitor.get_serial_number(),
            "400124190"
        )

    def test_get_pm_version(self):
        """
        PerformanceMonitor.get_pm_version - it should return the PM Version
        :return:
        """
        self.assertEqual(
            self.performance_monitor.get_pm_version(),
            "PM3"
        )

    def test_send_commands(self):
        """
        PerformanceMonitor.send_commands

        It should send commands to the Ergometer and return the response
        :return:
        """
        # It should return a Response object
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses([
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            }
        ])
        self.assertEqual(
            self.performance_monitor.send_commands([PerformanceMonitor.GET_STATUS]).__class__,
            Response
        )

    def test_get_status(self):
        """
        PerformanceMonitor.get_status - it should return a Response with the PM's status in
        :return:
        """
        # It should return a Response object
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses([
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            }
        ])
        self.assertEqual(
            self.performance_monitor.send_commands([PerformanceMonitor.GET_STATUS]).get_status(),
            2
        )

    def test_it_should_throw_bad_state_exception_if_manual_or_offline(self):
        """
        PerformanceMonitor.reset - it throw an exception if get status returns manual or offline
        :return:
        """
        # It should return a Response object
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses([
            {
                'CSAFE_GETSTATUS_CMD': [9]  # Offline state
            }
        ])

        self.assertRaises(BadStateException, self.performance_monitor.reset)

        self.assertEqual(
            PerformanceMonitor.KNOWN_PMS,
            {}
        )

    def test_it_should_throw_an_exception_if_waiting_for_finish_is_too_long(self):
        """
        PerformanceMonitor.reset - it should throw an exception if "Waiting for Finish" is too long
        :return:
        """
        PerformanceMonitor.RESET_RETRY_LIMIT = 2
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses([
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            }
        ])

        self.assertRaises(
            RetryLimitException,
            self.performance_monitor.reset
        )

    def test_it_should_throw_an_exception_if_waiting_for_idle_is_too_long(self):
        """
        PerformanceMonitor.reset - it should throw an exception if "Waiting for Idle" is too long
        :return:
        """
        PerformanceMonitor.RESET_RETRY_LIMIT = 2
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses([
            {
                'CSAFE_GETSTATUS_CMD': [7]  # Finish state
            },
            {
                'CSAFE_GETSTATUS_CMD': [7]  # Finish state
            },
            {
                'CSAFE_GETSTATUS_CMD': [7]  # Finish state
            },
            {
                'CSAFE_GETSTATUS_CMD': [7]  # Finish state
            }
        ])

        self.assertRaises(
            RetryLimitException,
            self.performance_monitor.reset
        )

    def test_it_should_throw_an_exception_if_waiting_for_ready_is_too_long(self):
        """
        PerformanceMonitor.reset - it should throw an exception if "Waiting for Ready" is too long
        :return:
        """
        PerformanceMonitor.RESET_RETRY_LIMIT = 2
        sys.modules['pyrow.csafe.cmd'].CsafeCmd.set_responses([
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            },
            {
                'CSAFE_GETSTATUS_CMD': [2]  # Idle state
            }
        ])

        self.assertRaises(
            RetryLimitException,
            self.performance_monitor.reset
        )
