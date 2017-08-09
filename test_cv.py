#Using Python3, openCV3

import cv2
import numpy as np
import time

cv2.namedWindow("cam", cv2.WINDOW_OPENGL)
cap = cv2.VideoCapture(0)

n = 100 # Number of loops to wait for time calculation
t = time.time()
# Capture frames from the camera
while True:


    ret, img = cap.read()
    if not ret:
        continue

    # convert to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # find edges and dilate. Nice & fast!
    # img = cv2.Canny(img, 100, 200)
    # img = cv2.dilate(img, np.ones((6, 6)))

    # OR...

    # # Adaptive thresholding. Too slow. :(
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # OR...

    # Otsu's thresholding. Nice & fast!
    # http://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
    values, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


    # Find contours and tree
    img, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find contours with at least x children. These must be qr markers!

    # Find markers that belong together

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