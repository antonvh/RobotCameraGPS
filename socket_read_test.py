import socket, sys, struct, threading
import time
try:
    import cPickle as pickle
except:
    import pickle

HOST = "127.0.0.1"
PORT = 50008
robot_positions = {}
running = True


def get_positions():
    global robot_positions, running
    connected = False
    while not connected:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Open socket to the location server
            s.connect((HOST, PORT))
        except:
            print("Connection failed. Trying again in 3s...")
            time.sleep(3)
            continue
        connected = True
        # continue # Keep trying
        print("connected")

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
            print(e)
            break
    s.close()

get_positions_thread = threading.Thread(target=get_positions)
get_positions_thread.start()

while 1:
    try:
        time.sleep(1)
        if len(robot_positions) > 0: print(robot_positions)
    except:
        print("Cleaning up")
        running = False
