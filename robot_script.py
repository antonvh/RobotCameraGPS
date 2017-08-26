#!/usr/bin/env python3

import socket, sys, struct
from threading import Thread
import time
import logging
from math import sin, cos
import numpy as np
import ev3dev.auto as ev3
try:
    import cPickle as pickle
except:
    import pickle


### Initialize ###
HOST = "127.0.0.1"  # Location server
PORT = 50008
RETRY_DELAY = 3     # Seconds
THIS_ROBOT = 1      # Our own ID
PI = 3.1415
TWO_PI = 2*PI
robot_positions = {}
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



### Position generators ###
def circle(origin, radius, step_px):
    circumference = radius * 2 * PI
    numsteps = int(circumference/step_px) + 1
    for i in range(numsteps):
        angle = 2 * PI / numsteps * i
        coord = np.array([cos(angle) * radius + origin[0], sin(angle) * radius + origin[1]])
        yield coord


### Get robot positions from server ###
def get_positions():
    global robot_positions, running
    connected = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not connected and running:
        try:
            # Open socket to the location server
            s.connect((HOST, PORT))
        except:
            logging.info("Connection to {1}:{2} failed. Trying again in {0}s...".format(RETRY_DELAY, HOST, PORT))
            time.sleep(RETRY_DELAY)
            continue        # Keep trying
        connected = True    # Because we got past trying
        logging.info("Connected to {0}:{1}".format(HOST, PORT))

    while running:
        try:
            buf = b''
            while len(buf) < 4:
                buf += s.recv(4 - len(buf))

            length = struct.unpack('!I', buf)[0]
            data = s.recv(length)  # read all data
            robot_positions = pickle.loads(data)
        except:
            e = sys.exc_info()[0]
            logging.warning(e)
            break

    if connected:
        s.close()


### Run the main loop ###
get_positions_thread = Thread(target=get_positions)
get_positions_thread.start()

positions = circle((500,500), 200, 10)
target = next(positions)

while 1:
    try:
        # Putting this in a try statement because we need to clean up after ctrl-c
        # Motor code goes here
        # time.sleep(1)
        if len(robot_positions) > 0: print(robot_positions)

        if THIS_ROBOT in robot_positions:
            heading = robot_positions[THIS_ROBOT]['heading']
            position = np.array(robot_positions[THIS_ROBOT]['position'])
            nose = np.array(robot_positions[THIS_ROBOT]['front'])

            # Calculate vector from nose to target
            path = target-nose
            if vec2d_length(path) <= 2:
                try:
                    target = next(positions)
                except:
                    break #no more points to be had
                path = target - nose
            target_direction = vec2d_angle(heading) - vec2d_angle(path)
            turnrate = clamp(vec2d_length(path) * sin(target_direction), (-400, 400))
            speed = clamp(vec2d_length(path) * cos(target_direction), (-300, 300))
            left_motor.run_forever(speed_sp=speed + turnrate)
            left_motor.run_forever(speed_sp=speed - turnrate)
        else:
            left_motor.stop()
            right_motor.stop()
    except:
        # Something went wrong or user aborted the script
        break

# Clean up
left_motor.stop()
right_motor.stop()
logging.info("Cleaning up")
running = False
