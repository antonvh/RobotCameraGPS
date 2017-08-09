import cv2
import time

cv2.namedWindow("cam", cv2.WINDOW_OPENGL)
cap = cv2.VideoCapture(0)

n = 100 # Number of loops to wait for time calculation
t = time.time()
# Capture frames from the camera
while True:


    ret, output = cap.read()
    if not ret:
        continue

    # convert to grayscale
    output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

    # find edges and dilate
    output = cv2.Canny(output, 100, 200)
    output = cv2.dilate(output, cv2.MORPH_RECT)

    # output = cv2.adaptiveThreshold(output, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    # Otsu's thresholding
    # http://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
    # values, output = cv2.threshold(output, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    output, contours, hierarchy = cv2.findContours(output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.imshow("cam", output)

    # Wait for the magic key
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