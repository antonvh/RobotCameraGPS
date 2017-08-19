#Using Python3, openCV3

import cv2
import numpy as np
import time
import zbarlight
from PIL import Image

cv2.namedWindow("cam", cv2.WINDOW_OPENGL)
cap = cv2.VideoCapture(0)

def atan2_vec(vector):
    return np.arctan2(vector[1], vector[0])/3.1415*180

n = 100 # Number of loops to wait for time calculation
t = time.time()
# Capture frames from the camera
qr_tags = []

while True:

    ok, img = cap.read()
    if not ok:
        continue # anyway

    # convert to grayscale
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # find edges and dilate. Nice & fast!
    # img_grey = cv2.Canny(img_grey, 100, 200)
    # img_grey = cv2.dilate(img_grey, np.ones((3, 3)))

    # OR...

    # Otsu's thresholding. Nice & fast!
    # http://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
    values, img_grey = cv2.threshold(img_grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours and tree
    img_grey, contours, hierarchy = cv2.findContours(img_grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find square contours with at least 2 children. These must be qr markers!
    markers = {}
    for x in range(0, len(contours)):

        k = x
        c = 0

        # Look for nested squares
        while (hierarchy[0][k][2] != -1):
            # As long as k has children [2], find that child and look for children again.
            # http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
            k = hierarchy[0][k][2]
            c = c + 1

        if hierarchy[0][k][2] != -1:
            c = c + 1

        if c >= 2:
            # To do: also check if it runs *exactly* 2 children deep. and not more.
            # This marker has at least two children. Now let's check if it's square.
            approx = cv2.approxPolyDP(contours[x], cv2.arcLength(contours[x], True)*0.02, True)
            if len(approx) == 4:
                # We found a squarish object
                # print(approx)
                a = approx[0][0]
                b = approx[1][0]
                c = approx[2][0]
                d = approx[3][0]
                center = (a+c)/2
                markers[x] = {'contour': approx,
                              'center': center,
                              'buddies': [],
                              'front': contours[hierarchy[0][hierarchy[0][x][2]][2]] #Sorry.
                              }

    for mkey in markers:
        marker = markers[mkey]
        # Calculate normalized vectors pointing to the two buddy markers from the main marker.
        # direction1 = (marker['center']-buddy1_c)
        # direction1 /= np.linalg.norm(direction1)
        # direction2 = (marker['center'] - buddy2_c)
        # direction2 /= np.linalg.norm(direction2)

        # The orientation wil be the sum of the two vectors + 135 degrees
        # orientation = atan2_vec(direction1 + direction2) + 135

        # The position is in the middle (average) of the two buddy markers.
        # Converting the float tuple to an int tuple with a list comprehension
        position = marker['center'].astype(int)

        # scale it up to include the whole code
        # qr_box = (qr_box * 1.55).astype(int)
        # movement_envelope = (qr_box * 1.1).astype(int)

        # put it back in place
        # qr_box += position
        # movement_envelope += position

        # check result
        cv2.drawContours(img, [marker['contour'], marker['front']], -1, (0, 0, 255), 3, lineType=cv2.LINE_4)

        # Draw the data
        cv2.putText(img, u"{0:.1f} deg {1}, code: {2}".format(0, position, 0), tuple(position),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)


    # Publish all data in a service on another thread, to which robots can connect.

    # Check all calculations in a preview window
    cv2.imshow("cam", img)

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


# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()