#Using Python3, openCV3

import cv2
import numpy as np
import time
from threading import Thread
import select, socket
try:
    import cPickle as pickle
except:
    import pickle
import logging

### Initialize ###

cv2.namedWindow("cam", cv2.WINDOW_OPENGL)
cap = cv2.VideoCapture(0)
robot_data = {}
PORT = 50007        # data port
RECV_BUFFER = 4096  # Block size
logging.basicConfig(filename='position_server.log',     # Filename
                    filemode='w',                       # Start each run with a fresh log
                    format='%(asctime)s, %(levelname)s, %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG, )              # Log info, debug and warning
running = True

### Helper functions ###
def atan2_vec(vector):
    return np.arctan2(vector[0], vector[1])


def vec_length(vector):
    return np.dot(vector, vector)**0.5


def pixel(img_grey, vector):
    if img_grey[vector[1], vector[0]]:
        return 1
    else:
        return 0


### Thread(s) ###

class SocketThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        # Initialize server socket
        self.connection_list = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", PORT))
        self.server_socket.listen(10)

    def run(self):
        global robot_data, running
        while running:
            try:
                # Get the list sockets which are ready to be read through select
                read_sockets, write_sockets, error_sockets = select.select(self.connection_list, [], [])
                for sock in read_sockets:

                    # New connection
                    if sock == self.server_socket:
                        # Handle the case in which there is a new connection recieved through server_socket
                        sockfd, addr = self.server_socket.accept()
                        self.connection_list.append(sockfd)
                        logging.info("Client %s connected" % addr)


                    # Some incoming message from a connected client
                    else:
                        # Data recieved from client, process it
                        try:
                            # In Windows, sometimes when a TCP program closes abruptly,
                            # a "Connection reset by peer" exception will be thrown

                            answer = ["OK"]
                            send_data = pickle.dumps(answer)
                            data = sock.recv(RECV_BUFFER)
                            sock.send(send_data)
                            rcvd_dict = pickle.loads(data)
                            logging.debug("Reveived socket data %s" % rcvd_dict)

                        # client disconnected, so remove it from socket list
                        except:
                            logging.info("Client %s is offline" % addr)
                            sock.close()
                            self.connection_list.remove(sock)
                            break
            except:
                logging.warning("Socket thread stopped unexpectedly")




n = 100 # Number of loops to wait for time calculation
t = time.time()
while True:

    ok, img = cap.read()
    if not ok:
        continue    #and try again.

    # convert to grayscale
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # print("read greyscale", t - time.time())
    # Otsu's thresholding. Nice & fast!
    # http://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
    # values, img_grey = cv2.threshold(img_grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    values, img_grey = cv2.threshold(img_grey, 100, 255, cv2.ADAPTIVE_THRESH_MEAN_C)

    # Find contours and tree
    img_grey, contours, hierarchy = cv2.findContours(img_grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # print("found contours", t - time.time())
    img = cv2.cvtColor(img_grey, cv2.COLOR_GRAY2BGR)

    # Find square contours with at least 2 children. These must be qr markers!
    markers = {}
    for x in range(0, len(contours)):

        k = x
        c = 0

        # Look for nested triangles
        while (hierarchy[0][k][2] != -1):
            # As long as k has children [2], find that child and look for children again.
            # http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
            k = hierarchy[0][k][2]
            c = c + 1

        if hierarchy[0][k][2] != -1:
            c = c + 1

        if c == 2:
            # To do: also check if it runs *exactly* 2 children deep. and not more.
            # This marker has at least two children. Now let's check if it's a triangle.
            approx = cv2.approxPolyDP(contours[x], cv2.arcLength(contours[x], True)*0.02, True)
            if len(approx) == 3:
                # We found a squarish object too.
                # Let it's corners be these vectors.
                a = approx[0][0]
                b = approx[1][0]
                c = approx[2][0]

                lengths = [vec_length(a-b), vec_length(b-c), vec_length(a-c)]
                shortest = min(lengths)
                shortest_idx = lengths.index(shortest)
                if shortest_idx == 0:
                    center = (a+b)/2
                    front = c
                elif shortest_idx == 1:
                    center = (c+b)/2
                    front = a
                else:   # shortest == 'ac':
                    center = (a+c)/2
                    front = b

                center = center.astype(int)
                direction = atan2_vec(front-center)

                # Now read code
                # Rotation matrix
                c = np.cos(direction)
                s = np.sin(direction)
                R = np.array([[-c, s], [-s, -c]])

                # Find the relative locations of the code dots
                # b1 = (center + np.dot(np.array([-0.375, 0.3]) * shortest, R)).astype(int)
                # b2 = (center + np.dot(np.array([-0.125, 0.3]) * shortest, R)).astype(int)
                # b3 = (center + np.dot(np.array([0.125, 0.3]) * shortest, R)).astype(int)
                # b4 = (center + np.dot(np.array([0.375, 0.3]) * shortest, R)).astype(int)
                # locations = [b1, b2, b3, b4]

                # Shorter notation:
                # locations = [(center + np.dot(np.array(l) * shortest, R)).astype(int) for l in [[-0.375, 0.3],
                #                                                                                 [-0.125, 0.3],
                #                                                                                 [0.125, 0.3],
                #                                                                                 [0.375, 0.3]]]

                # Even shorter with only linear algebra? Todo.
                relative_code_positions = np.array([[-0.375, 0.3],
                                                    [-0.125, 0.3],
                                                    [0.125, 0.3],
                                                    [0.375, 0.3]])
                locations = (center + np.dot(relative_code_positions * shortest, R)).astype(int)

                code = 0
                for i in range(4):
                    try:
                        p = img_grey[locations[i][1], locations[i][0]]
                    except:
                        code = -1
                        break
                    if not p:
                        code += 2**i

                # Check locations
                for l in locations:
                    cv2.circle(img, tuple(l), 4, (0, 255, 0), -1)

                # Draw the data
                cv2.putText(img, u"{0:.2f} rad, code: {1}".format(direction, code), tuple(center),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)


                markers[x] = {'contour': approx,
                              'center': center,
                              'front': front,
                              'direction': int(direction*180/3.1415),
                              'code': code
                              }

    # print("found markers", t - time.time())

    cv2.drawContours(img, [markers[x]['contour'] for x in markers], -1, (0, 0, 255), 3, lineType=cv2.LINE_4)




                # Publish all data in a service on another thread, to which robots can connect.

    # print("drawn contours", t - time.time())
    # Check all calculations in a preview window
    cv2.imshow("cam", img)

    # print("shown image", t - time.time())
    # Wait for the 'q' key. Dont use ctrl-c !!!
    keypress = cv2.waitKey(1) & 0xFF
    if keypress == ord('q'):
        break
    if n == 0:
        print("Looptime",(time.time()-t)/100)
        n = 100
        t = time.time()
        # break
    else:
        n -= 1

### clean up ###
running = False
