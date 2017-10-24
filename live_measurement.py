#!/usr/bin/python
import cv2
from imutils import perspective
from imutils import contours
import numpy as np
from scipy.spatial import distance as dist
import serial


def midpoint(ptA, ptB):
    return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5


# Constants
default_height = 100
image_width = 640
image_height = 480
height_width_const = 0.8085
cap = cv2.VideoCapture(0)
serial_path = '/dev/ttyUSB0'
while True:
    ser = serial.Serial(serial_path, baudrate=115200)
    height = int(ser.readline())
    print(height)
    # Take the height upto 2 meter
    if 0 < height < 200:
        # Set width and height of the camera
        # Start the camera
        ret = cap.set(3, image_width)
        ret = cap.set(4, image_height)
        ret, image = cap.read()

        # Filtering operations
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # Find contours of the image
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[1]
        (cnts, _) = contours.sort_contours(cnts)
        # Compute the pixel for each cm
        pixelsPerMetric = image_width / ((default_height-height) * height_width_const)
        # loop over the contours individually
        for c in cnts:
            # if the contour is not sufficiently large, ignore it
            if cv2.contourArea(c) < (((pixelsPerMetric * 10) ** 2) - 3000):
                continue

            # Compute the rotating bound of the box
            box = cv2.minAreaRect(c)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)

            # Corner points of the box
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr)
            (blbrX, blbrY) = midpoint(bl, br)
            (tlblX, tlblY) = midpoint(tl, bl)
            (trbrX, trbrY) = midpoint(tr, br)

            # Compute width and lenght of the object w.r.t pixel
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

            # Compute the size of the object in cm
            dimA = dA / pixelsPerMetric
            dimB = dB / pixelsPerMetric

            print('width = ' + str(dimA) + ' cm')
            print('length = ' + str(dimB) + ' cm')
            print('height = ' + str(height) + ' cm')
            print('volume = ' + str(dimA*dimB*height) + ' cm^3')
