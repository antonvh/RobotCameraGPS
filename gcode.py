import numpy as np

def gcode_parser(filename, max_segment_length=1000):
    pen = 0
    last_loc = np.array([0,0])
    with open(filename, 'r') as gfile:
        while 1:
            line = gfile.readline()
            if line == "": break
            got_coord = False
            data = line.split(" ")
            if data[0] == "G0":
                # Fast movement command
                for element in data:
                    if element[0] == "X":
                        x = float(element[1:])
                        got_coord = True
                    if element[0] == "Y":
                        y = float(element[1:])
                        got_coord = True
                    if element[0] == "Z":
                        z = float(element[1:])
                        if z > 0:
                            pen = 0
                        else:
                            pen = 1

                if got_coord:
                    loc = np.array([x, y])
                    last_loc = loc
                    yield loc, pen

            elif data[0] == "G1":
                # Precise movement command
                for element in data:
                    if element[0] == "X":
                        x = float(element[1:])
                        got_coord = True
                    if element[0] == "Y":
                        y = float(element[1:])
                        got_coord = True
                    if element[0] == "Z":
                        z = float(element[1:])
                        if z > 0:
                            pen = 0
                        else:
                            pen = 1

                if got_coord:
                    loc = np.array([x, y])
                    path = loc - last_loc
                    pathlength = np.dot(path, path)**0.5
                    # if pathlength < max_segment_length:
                    #     yield loc, pen
                    # else:
                    #Interpolate
                    steps = int(pathlength/max_segment_length)
                    for i in range(steps):
                        inbetween_loc = last_loc + (path / max_segment_length) * i
                        yield inbetween_loc, pen
                    yield loc, pen
                    last_loc = loc




if __name__ == '__main__':
    positions = gcode_parser('ev3.nc', max_segment_length=1)
    while 1:
        try:
            target = next(positions)
            print(target)
        except:
            raise  # no more points to be had