# This is an example file to show how to make use of pyrow
# Have the rowing machine on and plugged into the computer before starting the program
# The program will record Time, Distance, SPM, Pace, and Force Data for each
# stroke and save it to 'workout.csv'

import logging
import time

from pyrow.performance_monitor import PerformanceMonitor

if __name__ == '__main__':

    # Connecting to erg
    ergs = list(PerformanceMonitor.find())
    if len(ergs) == 0:
        exit("No ergs found.")

    erg = PerformanceMonitor(ergs[0])
    logging.info("Connected to erg")

    # Open and prepare file
    write_file = open('workout.csv', 'w')
    write_file.write('Time, Distance, SPM, Pace, Force Plot\n')

    # Loop until workout has begun
    workout = erg.get_workout()
    logging.info("Waiting for workout to start.")
    while workout.get_status() == 0:
        time.sleep(1)
        workout = erg.get_workout()
    logging.info("Workout has begun")

    # Loop until workout ends
    while workout.get_status() == 1:

        forceplot = erg.get_force_plot()
        # Loop while waiting for drive
        while forceplot.get_stroke_state() != 2 and workout.get_status() == 1:
            # TODO: sleep?
            forceplot = erg.get_force_plot()
            workout = erg.get_workout()

        # Record force data during the drive
        force = forceplot.get_force_plot()  # start of pull (when strokestate first changed to 2)
        monitor = erg.get_monitor()  # get monitor data for start of stroke
        # Loop during drive
        while forceplot.get_stroke_state == 2:
            # ToDo: sleep?
            forceplot = erg.get_force_plot()
            force.extend(forceplot.get_force_plot())

        forceplot = erg.get_force_plot()
        force.extend(forceplot.get_force_plot())

        # Write data to write_file
        workoutdata = str(monitor.get_time()) + "," + str(monitor.get_distance()) + "," + \
                      str(monitor.get_spm()) + "," + str(monitor.get_pace()) + ","

        forcedata = ",".join([str(f) for f in force])
        write_file.write(workoutdata + forcedata + '\n')

        # Get workout conditions
        workout = erg.get_workout()

    write_file.close()
    logging.info("Workout has ended.")
