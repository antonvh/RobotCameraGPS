#!/usr/bin/env python3

import socket, sys, struct
import logging,time
try:
    import cPickle as pickle
except:
    import pickle


### Initialize ###
PORT = 50008

### Get robot positions from server ###
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', PORT))

while 1:
    try:
        data, server = s.recvfrom(2048)
        robot_positions = pickle.loads(data)
        # delay = time.time()-robot_positions['time']
        # print(delay)
        print(robot_positions)
    except:
        e = sys.exc_info()[0]
        logging.warning(e)
        break



