#!/usr/bin/env python3

import socket, sys
from threading import Thread
import logging
from math import sin, cos
import numpy as np
import ev3dev.auto as ev3
try:
    import cPickle as pickle
except:
    import pickle


### Initialize ###
PORT = 50008
THIS_ROBOT = 2      # Our own ID
PI = 3.1415
TWO_PI = 2*PI
CIRCLE = 1
GO_TO_CENTER = 0
CENTER = np.array([1920/2, 1080/2])
MODE = GO_TO_CENTER

robot_broadcast_data = {'states':{},'balls':{},'settings':{}}
running = True
logging.basicConfig(  # filename='position_server.log',     # To a file. Or not.
    filemode='w',                                           # Start each run with a fresh log
    format='%(asctime)s, %(levelname)s, %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO, )                                   # Log info, and warning

left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
right_motor = ev3.LargeMotor(ev3.OUTPUT_C)


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


### Position generator ###
def circle(origin, radius, step_px):
    circumference = radius * 2 * PI
    numsteps = int(circumference/step_px) + 1
    for i in range(numsteps):
        angle = 2 * PI / numsteps * i
        coord = np.array([cos(angle) * radius + origin[0], sin(angle) * radius + origin[1]])
        yield coord


### Get robot positions from server ###
def get_positions():
    global robot_broadcast_data, running
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', PORT))

    while running:
        try:
            data, server = s.recvfrom(2048)
            robot_broadcast_data = pickle.loads(data)
        except:
            e = sys.exc_info()[0]
            logging.warning(e)
            raise

    s.close()


### Run the main loop ###
if __name__ == '__main__':
    get_positions_thread = Thread(target=get_positions)
    get_positions_thread.start()
    positions = circle((500, 500), 200, 10)

    if MODE == CIRCLE:
        target = next(positions)
    else:
        target = CENTER

    logging.info("Running")
    while 1:
        try:
            # We put this in a try statement because we need to clean up after ctrl-c
            if THIS_ROBOT in robot_broadcast_data['states']:
                center = np.array(robot_broadcast_data['states'][THIS_ROBOT][0])
                print(center, robot_broadcast_data['states'])
                nose = np.array(robot_broadcast_data['states'][THIS_ROBOT][1])
                heading = vec2d_angle(nose-center)

                #heading = robot_positions[THIS_ROBOT]['heading']
                #position = np.array(robot_positions[THIS_ROBOT]['center'])
                #nose = np.array(robot_positions[THIS_ROBOT]['front'])

                # Calculate vector from nose to target
                path = target-nose

                if MODE == CIRCLE:
                    if vec2d_length(path) <= 2:
                        try:
                            target = next(positions)
                        except:
                            break #no more points to be had
                        path = target - nose

                target_direction = vec2d_angle(path) - heading
                turnrate = clamp(vec2d_length(path) * sin(target_direction) * -1, (-500, 500))
                speed = clamp(vec2d_length(path) * cos(target_direction) * -2, (-500, 500))
                # print(",".join([str(x) for x in [speed, turnrate, position[0], position[1], nose[0], nose[1], target[0], target[1], target_direction*180/PI, heading*180/PI, vec2d_angle(path)*180/PI]]))
                left_motor.run_forever(speed_sp=(speed + turnrate))
                right_motor.run_forever(speed_sp=(speed - turnrate))
            else:
                left_motor.stop()
                right_motor.stop()
        except:
            e = sys.exc_info()[0]
            logging.warning(e)
            running = False
            left_motor.stop()
            right_motor.stop()
            logging.info("Cleaned up")
            # Something went wrong or user aborted the script
            raise

    # Clean up
    running = False
    left_motor.stop()
    right_motor.stop()
    logging.info("Cleaned up")