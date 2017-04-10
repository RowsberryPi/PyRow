"""
PyRow.Concept2.PerformanceMonitor
"""

import datetime
import logging
import sys
import time
from threading import Lock

import usb.util
from usb import USBError

from pyrow.csafe.cmd import CsafeCmd
from pyrow.exceptions import BadStateException, RetryLimitException
from pyrow.response import Response


class PerformanceMonitor(object):
    """
    PerformanceMonitor
    This class provides an interface between PyRow and a PyRow.Concept2 Performance Monitor device
    Example device:
    DEVICE ID 17a4:0001 on Bus 001 Address 004 =================
     bLength                :   0x12 (18 bytes)
     bDescriptorType        :    0x1 Device
     bcdUSB                 :  0x110 USB 1.1
     bDeviceClass           :    0x0 Specified at interface
     bDeviceSubClass        :    0x0
     bDeviceProtocol        :    0x0
     bMaxPacketSize0        :    0x8 (8 bytes)
     idVendor               : 0x17a4
     idProduct              : 0x0001
     bcdDevice              :  0x100 Device 1.0
     iManufacturer          :    0x1 PyRow.Concept2
     iProduct               :    0x2 PyRow.Concept2 Performance Monitor 3 (PM3)
     iSerialNumber          :    0x3 400124190
     bNumConfigurations     :    0x1
      CONFIGURATION 1: 98 mA ===================================
       bLength              :    0x9 (9 bytes)
       bDescriptorType      :    0x2 Configuration
       wTotalLength         :   0x29 (41 bytes)
       bNumInterfaces       :    0x1
       bConfigurationValue  :    0x1
       iConfiguration       :    0x0
       bmAttributes         :   0x80 Bus Powered
       bMaxPower            :   0x31 (98 mA)
        INTERFACE 0: Human Interface Device ====================
         bLength            :    0x9 (9 bytes)
         bDescriptorType    :    0x4 Interface
         bInterfaceNumber   :    0x0
         bAlternateSetting  :    0x0
         bNumEndpoints      :    0x2
         bInterfaceClass    :    0x3 Human Interface Device
         bInterfaceSubClass :    0x0
         bInterfaceProtocol :    0x0
         iInterface         :    0x0
          ENDPOINT 0x83: Interrupt IN ==========================
           bLength          :    0x7 (7 bytes)
           bDescriptorType  :    0x5 Endpoint
           bEndpointAddress :   0x83 IN
           bmAttributes     :    0x3 Interrupt
           wMaxPacketSize   :   0x40 (64 bytes)
           bInterval        :    0x2
          ENDPOINT 0x4: Interrupt OUT ==========================
           bLength          :    0x7 (7 bytes)
           bDescriptorType  :    0x5 Endpoint
           bEndpointAddress :    0x4 OUT
           bmAttributes     :    0x3 Interrupt
           wMaxPacketSize   :   0x40 (64 bytes)
           bInterval        :    0x1
    """
    VENDOR_ID = 0x17a4
    PM_VERSION = {
        0x0001: 'PM3',
        0x0002: 'PM4',
        0x0003: 'PM5'
    }

    MIN_FRAME_GAP = .050
    TIMEOUT = 2000

    STROKE_WAIT_MIN_SPEED = 0
    STROKE_WAIT_FOR_ACCELERATION = 1
    STROKE_DRIVE = 2
    STROKE_DWELLING = 3
    STROKE_RECOVERY = 4

    STATE_ERROR = 0
    STATE_READY = 1
    STATE_IDLE = 2
    STATE_HAVE_ID = 3
    STATE_NA = 4
    STATE_IN_USE = 5
    STATE_PAUSE = 6
    STATE_FINISHED = 7
    STATE_MANUAL = 8
    STATE_OFFLINE = 9

    SET_TIME = 'CSAFE_SETTIME_CMD'
    SET_DATE = 'CSAFE_SETDATE_CMD'

    GET_STATUS = 'CSAFE_GETSTATUS_CMD'
    GET_USER_ID = 'CSAFE_GETID_CMD'
    GET_WORKOUT_TYPE = 'CSAFE_PM_GET_WORKOUTTYPE'
    GET_WORKOUT_STATE = 'CSAFE_PM_GET_WORKOUTSTATE'
    GET_INTERVAL_TYPE = 'CSAFE_PM_GET_INTERVALTYPE'
    GET_INTERVAL_COUNT = 'CSAFE_PM_GET_WORKOUTINTERVALCOUNT'
    GET_TIME = 'CSAFE_PM_GET_WORKTIME'
    GET_DISTANCE = 'CSAFE_PM_GET_WORKDISTANCE'
    GET_CADENCE = 'CSAFE_GETCADENCE_CMD'
    GET_POWER = 'CSAFE_GETPOWER_CMD'
    GET_FORCE_PLOT_DATA = 'CSAFE_PM_GET_FORCEPLOTDATA'
    GET_STROKE_STATE = 'CSAFE_PM_GET_STROKESTATE'
    GET_STROKE_STATS = 'CSAFE_PM_GET_STROKESTATS'
    GET_PACE = 'CSAFE_GETPACE_CMD'
    GET_CALORIES = 'CSAFE_GETCALORIES_CMD'
    GET_HEART_RATE = 'CSAFE_GETHRCUR_CMD'
    GET_FW_VERSION = 'CSAFE_GETVERSION_CMD'
    GET_SERIAL = 'CSAFE_GETSERIAL_CMD'
    GET_CAPABILITIES = 'CSAFE_GETCAPS_CMD'

    GO_FINISHED = 'CSAFE_GOFINISHED_CMD'
    GO_IDLE = 'CSAFE_GOIDLE_CMD'
    GO_READY = 'CSAFE_GOREADY_CMD'
    GO_IN_USE = 'CSAFE_GOINUSE_CMD'
    RESET = 'CSAFE_RESET_CMD'

    SET_WORKOUT = 'CSAFE_SETTWORK_CMD'
    SET_HORIZONTAL = 'CSAFE_SETHORIZONTAL_CMD'
    SET_SPLIT_DURATION = 'CSAFE_PM_SET_SPLITDURATION'
    SET_POWER = 'CSAFE_SETPOWER_CMD'
    SET_PROGRAM = 'CSAFE_SETPROGRAM_CMD'

    GET_ERG_INFORMATION = [GET_FW_VERSION, GET_SERIAL, GET_CAPABILITIES, 0x00]
    GET_WORKOUT = [GET_USER_ID, GET_WORKOUT_TYPE, GET_WORKOUT_STATE,
                   GET_INTERVAL_TYPE, GET_INTERVAL_COUNT]
    GET_FORCE_PLOT = [GET_FORCE_PLOT_DATA, 32, GET_STROKE_STATE]
    GET_SCREEN = [GET_TIME, GET_DISTANCE, GET_CADENCE, GET_POWER, GET_CALORIES, GET_HEART_RATE]
    GET_EXTRA_METRICS = [GET_STROKE_STATS, 32, GET_STROKE_STATE]

    RESET_RETRY_LIMIT = 10
    RESET_WAIT_MAX = 0.5

    KNOWN_PMS = {}

    @staticmethod
    def find():
        ergs = usb.core.find(find_all=True, idVendor=PerformanceMonitor.VENDOR_ID)
        pms = []
        for erg in ergs:
            if erg.serial_number not in PerformanceMonitor.KNOWN_PMS:
                PerformanceMonitor.KNOWN_PMS[erg.serial_number] = erg
                pms.append(PerformanceMonitor(erg))
        return pms

    def __init__(self, device):
        """
        :param Device device:
        :return:
        """
        self.__device = device
        if sys.platform != 'win32':
            if device.is_kernel_driver_active(0):
                device.detach_kernel_driver(0)
            else:
                logging.debug('USB Kernel driver not on %s', sys.platform)

        usb.util.claim_interface(device, 0)

        try:
            device.set_configuration()
        except USBError:
            pass

        interface = device[0][(0, 0)]
        self.__in_address = interface[0].bEndpointAddress
        self.__out_address = interface[1].bEndpointAddress

        self.__manufacturer = usb.util.get_string(self.__device, self.__device.iManufacturer)
        self.__product = usb.util.get_string(self.__device, self.__device.iProduct)
        self.__serial_number = usb.util.get_string(self.__device, self.__device.iSerialNumber)

        self.__last_message = time.time()
        self.__lock = Lock()

        self.reset()

    def set_clock(self):
        """
        Sets the date and time on the Performance Monitor to match the computer
        :return:
        """
        now = datetime.datetime.now()

        command = [self.SET_TIME, now.hour, now.minute, now.second]
        command.extend([self.SET_DATE, (now.year - 1900), now.month, now.day])

        self.send_commands(command)

    def get_manufacturer(self):
        """
        :return string:
        """
        return self.__manufacturer

    def get_product(self):
        """
        :return string:
        """
        return self.__product

    def get_serial_number(self):
        """
        :return string:
        """
        return self.__serial_number

    def get_pm_version(self):
        """
        :return string:
        """
        return self.PM_VERSION[self.__device.idProduct]

    def send_commands(self, commands):
        """
        :param [] commands:
        :return Response:
        """
        self.__lock.acquire()
        now = time.time()
        delta = now - self.__last_message
        if delta < self.MIN_FRAME_GAP:
            time.sleep(self.MIN_FRAME_GAP - delta)

        try:
            c_safe = CsafeCmd.write(commands)

            length = self.__device.write(self.__out_address, c_safe, timeout=self.TIMEOUT)
            self.__last_message = time.time()

            response = []
            while not response:
                transmission = self.__device.read(self.__in_address, length, timeout=20000)
                response = CsafeCmd.read(transmission)
        except Exception as ex:
            del self.KNOWN_PMS[self.__serial_number]
            usb.util.release_interface(self.__device, 0)
            raise ex

        self.__lock.release()

        return Response(response)

    def get_monitor(self, force_plot=False, extra_metrics=False):
        """
        Returns values from the monitor that relate to the current workout,
        optionally returns force plot data and stroke state
        :return Response:
        """
        command = self.GET_SCREEN

        if force_plot:
            command.extend(self.GET_FORCE_PLOT)

        if extra_metrics:
            command.extend(self.GET_EXTRA_METRICS)

        return self.send_commands(command)

    def get_force_plot(self):
        """
        Returns force plot data and stroke state
        :return Response:
        """
        return self.send_commands(self.GET_FORCE_PLOT)

    def get_workout(self):
        """
        Returns overall workout data
        :return Response:
        """
        return self.send_commands(self.GET_WORKOUT)

    def get_erg(self):
        """
        Returns all erg data that is not related to the workout
        :return Response:
        """
        return self.send_commands(self.GET_ERG_INFORMATION)

    def get_status(self):
        """
        Gets the current status from the Performance Monitor
        :return Response:
        """
        response = self.send_commands([
            self.GET_STATUS
        ])

        manual = response.get_status() == self.STATE_MANUAL
        offline = response.get_status() == self.STATE_OFFLINE

        if manual or offline:
            del self.KNOWN_PMS[self.__serial_number]
            usb.util.release_interface(self.__device, 0)
            raise BadStateException(self, response.get_status_message())

        return response

    def reset(self):
        """
        Resets the Performance Monitor or throws an Exception if unable to
        :return:
        """
        response = self.get_status()
        logging.debug('Current Status: %s on %s', response.get_status_message(),
                      self.__serial_number)

        manual = response.get_status() == self.STATE_MANUAL
        offline = response.get_status() == self.STATE_OFFLINE

        if manual or offline:
            del self.KNOWN_PMS[self.__serial_number]
            usb.util.release_interface(self.__device, 0)
            raise BadStateException(self, response.get_status_message())

        finished = response.get_status() == self.STATE_FINISHED
        ready = response.get_status() == self.STATE_READY

        if not finished and not ready:
            self.send_commands([self.GO_FINISHED])
            retries = 0
            while True:
                status = self.get_status().get_status()
                if status == self.STATE_FINISHED:
                    logging.debug('Finished: %s', self.__serial_number)
                    break
                else:
                    logging.debug('Waiting for Finish (currently: %d) %d/%d on %s', status,
                                  retries, self.RESET_RETRY_LIMIT, self.__serial_number)
                    time.sleep(self.MIN_FRAME_GAP)
                    retries += 1
                    if retries >= self.RESET_RETRY_LIMIT:
                        raise RetryLimitException(
                            'Not Finished on {0}, got {1}'.format(self.__serial_number, status))

        self.send_commands([self.GO_IDLE])
        retries = 0
        while True:
            status = self.get_status().get_status()
            if status == self.STATE_IDLE:
                logging.debug('Idle: %s', self.__serial_number)
                break
            else:
                logging.debug('Waiting for Idle (currently: %d) %d/%d on %s', status,
                              retries, self.RESET_RETRY_LIMIT, self.__serial_number)
                time.sleep(self.MIN_FRAME_GAP)
                retries += 1
                if retries >= self.RESET_RETRY_LIMIT:
                    raise RetryLimitException(
                        'Not Idle on {0}, got {1}'.format(self.__serial_number, status))

        self.send_commands([self.GO_READY])
        retries = 0
        while True:
            status = self.get_status().get_status()
            if status == self.STATE_READY:
                logging.debug('Ready: %s', self.__serial_number)
                break
            else:
                logging.debug('Waiting for Ready (currently: %d) %d/%d on %s', status,
                              retries, self.RESET_RETRY_LIMIT, self.__serial_number)
                time.sleep(self.MIN_FRAME_GAP)
                retries += 1
                if retries >= self.RESET_RETRY_LIMIT:
                    raise RetryLimitException(
                        'Not Ready on {0}, got {1}'.format(self.__serial_number, status))

    def set_workout(self,
                    program=None,
                    workout_time=None,
                    distance=None,
                    split=None,
                    pace=None,
                    cal_pace=None,
                    power_pace=None):
        """
        If machine is in the ready state, function will set the
        workout and display the start workout screen
        """

        self.reset()
        time.sleep(self.RESET_WAIT_MAX)
        command = []

        # Set Workout Goal
        program_num = 0
        if program is not None:
            self.__validate_value(program, 'Program', 0, 15)
            program_num = program
        elif workout_time is not None:
            if len(workout_time) == 1:
                # if only seconds in workout_time then pad minutes
                workout_time.insert(0, 0)
            if len(workout_time) == 2:
                # if no hours in workout_time then pad hours
                workout_time.insert(0, 0)
            self.__validate_value(workout_time[0], 'Time Hours', 0, 9)
            self.__validate_value(workout_time[1], 'Time Minutes', 0, 59)
            self.__validate_value(workout_time[2], 'Time Seconds', 0, 59)

            if workout_time[0] == 0 and workout_time[1] == 0 and workout_time[2] < 20:
                # checks if workout is < 20 seconds
                raise ValueError('Workout too short on {0}'.format(self.__serial_number))

            command.extend([self.SET_WORKOUT, workout_time[0],
                            workout_time[1], workout_time[2]])

        elif distance is not None:
            self.__validate_value(distance, 'Distance', 100, 50000)
            command.extend([self.SET_HORIZONTAL, distance, 36])  # 36 = meters

        # Set Split
        if split is not None:
            if workout_time is not None and program is None:
                split_time = int(split * 100)
                # total workout workout_time (1 sec)
                time_raw = workout_time[0] * 3600 + workout_time[1] * 60 + workout_time[2]
                # split workout_time that will occur 30 workout_times (.01 sec)
                min_split = int(time_raw / 30 * 100 + 0.5)
                self.__validate_value(
                    split_time,
                    'Split Time',
                    max(2000, min_split),
                    time_raw * 100
                )
                command.extend([self.SET_SPLIT_DURATION, 0, split_time])
            elif distance is not None and program is None:
                # split distance that will occur 30 workout_times (m)
                min_split = int(distance / 30 + 0.5)
                self.__validate_value(split, 'Split distance', max(100, min_split), distance)
                command.extend([self.SET_SPLIT_DURATION, 128, split])
            else:
                raise ValueError(
                    'Cannot set split for current goal on {0}'.format(self.__serial_number))

        # Set Pace
        if pace is not None:
            power_pace = int(round(2.8 / ((pace / 500.) ** 3)))
        elif cal_pace is not None:
            power_pace = int(round((cal_pace - 300.) / (4.0 * 0.8604)))
        if power_pace is not None:
            command.extend([self.SET_POWER, power_pace, 88])  # 88 = watts

        command.extend([self.SET_PROGRAM, program_num, 0, self.GO_IN_USE])

        self.send_commands(command)
        time.sleep(self.RESET_WAIT_MAX)

        if not self.__wait_for_workout(command, workout_time, distance):
            logging.warning('Failed to set workout on %s', self.__serial_number)
            self.set_workout(
                program,
                workout_time,
                distance,
                split,
                pace,
                cal_pace,
                power_pace
            )

    @staticmethod
    def __validate_value(value, label, minimum, maximum):
        """
        Checks that value is an integer and within the specified range
        """
        if not isinstance(value, int):
            raise TypeError(label)
        if not minimum <= value <= maximum:
            raise ValueError(label + ' outside of range')
        return True

    def __wait_for_workout(self, command, workout_time, distance, max_attempts=25):
        """
        :param command:
        :param workout_time:
        :param distance:
        :return:
        """
        attempts = 0
        while attempts < max_attempts:
            in_use = self.get_status().get_status() == self.STATE_IN_USE

            if self.SET_HORIZONTAL in command and in_use:
                erg_distance = self.send_commands([self.GET_DISTANCE]).get_distance()
                if erg_distance == distance:
                    logging.debug('Workout set on erg %s in %ds', self.__serial_number,
                                  attempts * self.RESET_WAIT_MAX)
                    return True
                logging.debug('Erg %d Distance: %d, expected: %d. Try %d/%d', self.__serial_number,
                              erg_distance, distance, attempts, max_attempts)

            elif self.SET_WORKOUT in command and in_use:
                length = workout_time[0] * 60 * 60 + workout_time[1] * 60 + workout_time[2]
                erg_time = self.send_commands([self.GET_TIME]).get_time()
                if erg_time == length:
                    logging.debug('Workout set on erg %s in %ds', self.__serial_number,
                                  attempts * self.RESET_WAIT_MAX)
                    return True
                logging.debug('Erg %d Distance: %d, expected: %d. Try %d/%d', self.__serial_number,
                              erg_time, length, attempts, max_attempts)

            time.sleep(self.RESET_WAIT_MAX)

            attempts += 1
        return False
