#import the libraries
import cv2 as cv
import numpy as np
import depthai as dai
#import imutils

#HSV_LOW = [160, 100, 50]
#HSV_HIGH = [180, 255, 255]
HSV_LOW = [153, 118, 77]
HSV_HIGH = [255, 255, 255]

#def setHSV_LOW(val, index):
#	HSV_LOW[index] = val
#def setHSV_HGIH(val, index):
#	HSV_HIGH[index] = val

#def callback(x):
#    #assign trackbar position value to H,S,V High and low variable
#    HSV_LOW[0] = cv.getTrackbarPos('hsv_low_h','Track')
#    HSV_LOW[1] = cv.getTrackbarPos('hsv_low_v','Track')
#    HSV_LOW[2] = cv.getTrackbarPos('hsv_low_s','Track')
#    HSV_HIGH[0] = cv.getTrackbarPos('hsv_high_h','Track')
#    HSV_HIGH[1] = cv.getTrackbarPos('hsv_high_s','Track')
#    HSV_HIGH[2] = cv.getTrackbarPos('hsv_high_v','Track')

#cv.namedWindow("Track", cv.WINDOW_NORMAL)
#cv.createTrackbar('hsv_low_h','Track', 160, 180, callback)
#cv.createTrackbar('hsv_low_v','Track', 100, 255, callback)
#cv.createTrackbar('hsv_low_s','Track', 50, 255, callback)
#cv.createTrackbar('hsv_high_h','Track', 180, 180, callback)
#cv.createTrackbar('hsv_high_v','Track', 15, 255, callback)
#cv.createTrackbar('hsv_high_s','Track', 15, 255, callback)

# Create pipeline
pipeline = dai.Pipeline()

# Define source and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
manip = pipeline.create(dai.node.ImageManip)
manip.initialConfig.setResize(320,180)
manip.initialConfig.setFrameType(dai.ImgFrame.Type.BGR888p)
xoutVideo = pipeline.create(dai.node.XLinkOut)
xoutVideo.setStreamName("video")

# Linking
camRgb.video.link(manip.inputImage)
manip.out.link(xoutVideo.input)
# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(True)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(12)
# camRgb.setIspScale(9,16)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

# capture frames from a camera 
# cap = cv.VideoCapture(1) 
	video = device.getOutputQueue('video', maxSize=8, blocking=False)

	img_data = []

	while(True):
		videoFrame = video.get()
		# reads frames from a camera 
		# ret, img = cap.read()
		img = videoFrame.getCvFrame()
		

		#convert the BGR image to HSV colour space
		hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
		#obtain the grayscale image of the original image
		gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		gray = cv.medianBlur(gray, 5)
		#set the bounds for the red hue
		lower_red = np.array(HSV_LOW)
		upper_red = np.array(HSV_HIGH)

		#create a mask using the bounds set
		mask = cv.inRange(hsv, lower_red, upper_red)
		#create an inverse of the mask
		mask_inv = cv.bitwise_not(mask)
		#Filter only the red colour from the original image using the mask(foreground)
		res = cv.bitwise_and(img, img, mask=mask)
		#Filter the regions containing colours other than red from the grayscale image(background)
		background = cv.bitwise_and(gray, gray, mask = mask_inv)
		#convert the one channelled grayscale background to a three channelled image
		background = np.stack((background,)*3, axis=-1)
		#add the foreground and the background
		added_img = cv.add(res, background)

		# Filter Smoothing
		mask = cv.bilateralFilter(mask, 9, 75, 75)
		# Contouring, done on color mask
		frame = cv.cvtColor(mask, cv.COLOR_BGR2RGB)
		g = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
		edge = cv.Canny(g, 140, 210)

		contours, hierarchy = cv.findContours(edge, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

		for c in contours:
			area = cv.contourArea(c)
			if area < 10:
				cv.fillPoly(edge, pts=[c], color=0)
				continue

		edge = cv.morphologyEx(edge, cv.MORPH_CLOSE, cv.getStructuringElement(cv.MORPH_ELLIPSE, (51,51)));


		contours, hierarchy = cv.findContours(edge, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)


		#for c in contours:
		#	if cv.contourArea(c) > 500:
		#		hull = cv.convexHull(c)
		#		cv.drawContours(added_img, [hull], 0, (0,255,0), 2)

		for c in contours:
			area = cv.contourArea(c)
			if area < 500:
				cv.fillPoly(edge, pts=[c], color=0)
				continue

			rect = cv.minAreaRect(c)
			box = cv.boxPoints(rect)
			box = np.int0(box)

			cv.drawContours(added_img, [box], 0, (0,255,0), 1)



		cv.namedWindow('Contours', cv.WINDOW_NORMAL)
		cv.imshow('Contours', added_img)


		#create resizable windows for the images
		#cv.namedWindow("res", cv.WINDOW_NORMAL)
		#cv.namedWindow("hsv", cv.WINDOW_NORMAL)
		#cv.namedWindow("mask", cv.WINDOW_NORMAL)
		#cv.namedWindow("added", cv.WINDOW_NORMAL)
		#cv.namedWindow("back", cv.WINDOW_NORMAL)
		#cv.namedWindow("mask_inv", cv.WINDOW_NORMAL)
		#cv.namedWindow("gray", cv.WINDOW_NORMAL)

		#display the images
		#cv.imshow("back", background)
		#cv.imshow("mask_inv", mask_inv)
		#cv.imshow("added",added_img)
		#cv.imshow("mask", mask)
		#cv.imshow("gray", gray)
		#cv.imshow("hsv", hsv)
		#cv.imshow("res", res)
		if cv.waitKey(1) & 0xFF == ord('q'):
			break

	cv.destroyAllWindows()




