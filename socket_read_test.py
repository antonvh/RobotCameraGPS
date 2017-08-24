import socket

try:
    import cPickle as pickle
except:
    import pickle

HOST = "127.0.0.1"
PORT = 50008

# Open socket to the location server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while 1:
    try:
        data = s.recv(1024*4)  # read all data
        rcv = pickle.loads(data)
        print(rcv)

    except:
        print("oops")
        break