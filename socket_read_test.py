#!/usr/bin/env python3

import socket, sys, struct
from threading import Thread
import time
import logging
try:
    import cPickle as pickle
except:
    import pickle


### Initialize ###
HOST = "127.0.0.1"  # Location server
PORT = 50008
RETRY_DELAY = 3     # Seconds
THIS_ROBOT = 1      # Our own ID
robot_positions = {}
running = True
logging.basicConfig(  # filename='position_server.log',     # To a file. Or not.
    filemode='w',                                           # Start each run with a fresh log
    format='%(asctime)s, %(levelname)s, %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO, )                                   # Log info, and warning


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
while 1:
    try:
        # Putting this in a try statement because we need to clean up after ctrl-c
        # Motor code goes here
        time.sleep(1)
        if len(robot_positions) > 0: print(robot_positions)
    except:
        # Something went wrong or user aborted the script
        logging.info("Cleaning up")
        running = False
        break
