# Program for 'AI Enabled Car Parking using Opencv
# Load packages

# Capturing video using opencv
import cv2
# python object file to byte stream
import pickle
# cv zone
import cvzone
import numpy as np

# Video capturing feed
cap = cv2.VideoCapture('carPark.mp4')

# Statement
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

# Width and height of the image
width, height = 107, 48



#def function
def checkParkingSpace(imgPro):
    spaceCounter = 0

# POS--> POSITION OF A STRING IN ANOTHER STRING
    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]

# cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)

# if condition:
        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2
# drawing a rectangle image

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))
# while Condition:

while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

# checkParkingSpace
    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)

# cv2.waitKey in mileseconds

    cv2.waitKey(10)