#!/usr/bin/env python3

import socket, sys
from threading import Thread
from gcode import gcode_parser
import logging
from math import sin, cos
import numpy as np
import ev3dev.auto as ev3

try:
    import cPickle as pickle
except:
    import pickle


### Initialize ###
SPEED_MAX = 300

TURN_MAX = 200

SPEED_P = 2

TURN_P = 1

PORT = 50008

THIS_ROBOT = 1      # Our own ID

PI = 3.1415

TWO_PI = 2*PI

GCODE_SCALE = 10 # Generating gcode in mm and then scaling it up to reduce excess preciosion

INTERPOLATION = 2 # Max length (in mm!) between two points

PEN_ACTIVE = 1

PEN_DOWN = -150

robot_positions = {}
running = True
logging.basicConfig(  # filename='position_server.log',     # To a file. Or not.
    filemode='w',                                           # Start each run with a fresh log
    format='%(asctime)s, %(levelname)s, %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO, )                                   # Log info, and warning

left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
right_motor = ev3.LargeMotor(ev3.OUTPUT_C)
if PEN_ACTIVE:
    pen_motor = ev3.MediumMotor(ev3.OUTPUT_A)

### Helpers ###
def vec2d_length(vector):
    return np.dot(vector, vector)**0.5

def vec2d_angle(vector):
    return np.arctan2(vector[1], vector[0])

def clamp(n, range):
    """
    Given a number and a range, return the number, or the extreme it is closest to.

    :param n: number
    :return: number
    """
    minn, maxn = range
    return max(min(maxn, n), minn)


### Get robot positions from server ###
def get_positions():
    global robot_positions, running
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', PORT))

    while running:
        try:
            data, server = s.recvfrom(2048)
            robot_positions = pickle.loads(data)
        except:
            e = sys.exc_info()[0]
            logging.warning(e)
            raise

    s.close()


### Run the main loop ###
get_positions_thread = Thread(target=get_positions)
get_positions_thread.start()

positions = gcode_parser('ev3.nc', max_segment_length=INTERPOLATION)
target, pen = next(positions)
target = target * GCODE_SCALE

while 1:
    try:
        # Putting this in a try statement because we need to clean up after ctrl-c

        if THIS_ROBOT in robot_positions:
            if (not pen) and PEN_ACTIVE:
                pen_motor.run_to_abs_pos(position_sp=0, speed_sp=400, stop_action="brake")
                pen_motor.wait_while("running")
            if pen and PEN_ACTIVE:
                pen_motor.run_to_abs_pos(position_sp=PEN_DOWN, speed_sp=400, stop_action="brake")
                pen_motor.wait_while("running")

            heading = robot_positions[THIS_ROBOT]['heading']
            position = np.array(robot_positions[THIS_ROBOT]['center'])
            nose = np.array(robot_positions[THIS_ROBOT]['front'])

            # Calculate vector from nose to target
            path = target-nose

            if vec2d_length(path) <= 2:
                # Try to get a new target if we're close enough to the current one.
                try:
                    target, pen = next(positions)
                    target = target * GCODE_SCALE
                except:
                    # We've run of targets
                    break
                path = target - nose

            target_direction = vec2d_angle(path) - heading
            turnrate = clamp(vec2d_length(path) * sin(target_direction) * -TURN_P, (-TURN_MAX, TURN_MAX))
            speed = clamp(vec2d_length(path) * cos(target_direction) * -SPEED_P, (-SPEED_MAX, SPEED_MAX))
            left_motor.run_forever(speed_sp=(speed + turnrate))
            right_motor.run_forever(speed_sp=(speed - turnrate))
        else:
            left_motor.stop()
            right_motor.stop()
    except:
        e = sys.exc_info()[0]
        logging.warning(e)
        # Something went wrong or user aborted the script
        break

# Clean up
left_motor.stop()
right_motor.stop()
logging.info("Cleaning up")
running = False
