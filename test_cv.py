#Using Python3, openCV3

import cv2
import numpy as np
import time

def center(contour):
    # print(contour[0][0])
    return (contour[0][0][0]+contour[2][0][0])/2, (contour[0][0][1]+contour[2][0][1])/2

cv2.namedWindow("cam", cv2.WINDOW_OPENGL)
cap = cv2.VideoCapture(0)

n = 100 # Number of loops to wait for time calculation
t = time.time()
# Capture frames from the camera
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

    # # Adaptive thresholding. Too slow. :(
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # OR...

    # Otsu's thresholding. Nice & fast!
    # http://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
    values, img_grey = cv2.threshold(img_grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


    # Find contours and tree
    img_grey, contours, hierarchy = cv2.findContours(img_grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find square contours with at least 2 children. These must be qr markers!
    markers = []
    for x in range(0, len(contours)):

        k = x
        c = 0

        # Look for nested squares
        while (hierarchy[0][k][2] != -1):
            # As long as k has children [2], find that child and look for children again.
            k = hierarchy[0][k][2]
            c = c + 1

        if hierarchy[0][k][2] != -1:
            c = c + 1

        if c >= 2:
            approx = cv2.approxPolyDP(contours[x], cv2.arcLength(contours[x], True)*0.02, True)
            # approxPolyDP(Mat(contours[i]), approx, arcLength(Mat(contours[i]), true) * 0.02, true);
            if len(approx) == 4:
                # print(approx)
                markers += {'id': x,
                            'contour': approx,
                            'center': center(approx)
                            }
                print(center(approx))
                cv2.drawContours(img, [approx], -1, (0,0,255), 3, lineType=cv2.LINE_4)

    # Find markers that belong together
    for m in markers:
        pass
        # Calculate list of buddy positions (aligned & within distance)
        # Check list of markers against buddy list
        # See if we can find two other buddy markers

    # Calculate their positions and rotations using moments

    # Read their qr codes just once (expensive!) and then track them frame-to-frame.

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