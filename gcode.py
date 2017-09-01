def gcode_parser(filename):
    pen = 0
    with open(filename, 'r') as gfile:
        while 1:
            line = gfile.readline()
            if line == "": break
            got_coord = False
            data = line.split(" ")
            if data[0] == "G1" or data[0] == "G0":
                # Movement command
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
                    yield x, y, pen


