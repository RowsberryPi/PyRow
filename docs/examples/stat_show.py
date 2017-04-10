# This is an example file to show how to make use of pyrow
# Have the rowing machine on and plugged into the computer before starting the program
# The program will display any changes to the machine status, stroke state, or workout state

import logging
import time

from pyrow.performance_monitor import PerformanceMonitor

if __name__ == '__main__':
    # Connecting to erg
    ergs = list(PerformanceMonitor.find())
    if len(ergs) == 0:
        exit('No ergs found.')
    erg = PerformanceMonitor(ergs[0])
    logging.info('Connected to erg.')

    # Create a dictionary of the different status states
    state = ['Error', 'Ready', 'Idle', 'Have ID', 'N/A', 'In Use',
             'Pause', 'Finished', 'Manual', 'Offline']

    stroke = ['Wait for min speed', 'Wait for acceleration', 'Drive', 'Dwelling', 'Recovery']

    workout = ['Waiting begin', 'Workout row', 'Countdown pause', 'Interval rest',
               'Work time inverval', 'Work distance interval', 'Rest end time', 'Rest end distance',
               'Time end rest', 'Distance end rest', 'Workout end', 'Workout terminate',
               'Workout logged', 'Workout rearm']

    command = ['CSAFE_GETSTATUS_CMD', 'CSAFE_PM_GET_STROKESTATE', 'CSAFE_PM_GET_WORKOUTSTATE']

    # prime status number
    cstate = -1
    cstroke = -1
    cworkout = -1

    erg.set_workout(distance=2000, split=100, pace=120)

    # Inf loop
    while 1:
        results = erg.send_commands(command)
        if cstate != (results['CSAFE_GETSTATUS_CMD'][0] & 0xF):
            cstate = results['CSAFE_GETSTATUS_CMD'][0] & 0xF
            logging.debug('State %s: %s', str(cstate), state[cstate])
        if cstroke != results['CSAFE_PM_GET_STROKESTATE'][0]:
            cstroke = results['CSAFE_PM_GET_STROKESTATE'][0]
            logging.debug('Stroke %s: %s', str(cstroke), stroke[cstroke])
        if cworkout != results['CSAFE_PM_GET_WORKOUTSTATE'][0]:
            cworkout = results['CSAFE_PM_GET_WORKOUTSTATE'][0]
            logging.debug('Workout %s: %s', str(cworkout), workout[cworkout])
        time.sleep(1)
