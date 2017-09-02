import socket
import sys,time
try:
    import cPickle as pickle
except:
    import pickle

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
PORT = 50008

# Bind the socket to the broadcast port
server_address = ('255.255.255.255', PORT)

while True:
    data = pickle.dumps({'time': time.time()})
    if data:
        try:
            sent = sock.sendto(data, server_address)
            # print(sent)
            time.sleep(0.025)
        except OSError as exc:
            if exc.errno == 55:
                time.sleep(0.1)
            else:
                raise