#import the libraries
import cv2 as cv
import numpy as np
import depthai as dai
from collections import deque

# color detection bounds
#HSV_LOW = [160, 100, 50]
#HSV_HIGH = [180, 255, 255]
HSV_LOW = [153, 118, 77]
HSV_HIGH = [255, 255, 255]

# Aspect Ratio Bounds
ASPECT_UPPER = 1.5
ASPECT_LOWER = 0.8
BUFFER_SIZE = 13 # Increasing Buffer improves accuracy, but uses memory


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

class Vision:
	def __init__(self):
		# Create pipeline
		self.pipeline = dai.Pipeline()
		pipeline = self.pipeline

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
		camRgb.setFps(24)
		# camRgb.setIspScale(9,16)

	def red_detection(self):
		count = 0

		pipeline = self.pipeline

		# Connect to device and start pipeline
		with dai.Device(pipeline) as device:

		# capture frames from a camera 
		# cap = cv.VideoCapture(1) 
			video = device.getOutputQueue('video', maxSize=8, blocking=False)

			img_buf = deque()
			aspect_sum = 0

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
				# Detect only edges
				edge = cv.Canny(g, 140, 210)

				# Get Contours from of edges, (external = don't detect contours within contours)
				contours, hierarchy = cv.findContours(edge, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

				# for those contours with an area less than 10, fill in (remove) them
				#	removes static and decreases artifact detection
				for c in contours:
					area = cv.contourArea(c)
					if area < 10:
						cv.fillPoly(edge, pts=[c], color=0)
						continue

				# merge small and near by contours
				#	some contours aren't detected in one connected clear contour, this treats that issue
				edge = cv.morphologyEx(edge, cv.MORPH_CLOSE, cv.getStructuringElement(cv.MORPH_ELLIPSE, (51,51)));

				# get the now new contours
				contours, hierarchy = cv.findContours(edge, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)


				#for c in contours:
				#	if cv.contourArea(c) > 500:
				#		hull = cv.convexHull(c)
				#		cv.drawContours(added_img, [hull], 0, (0,255,0), 2)


				# for those contours with an area less than 500, fill in (remove) them
				#	size detection calibration essentially			
				for c in contours:
					area = cv.contourArea(c)
					if area < 500:
						cv.fillPoly(edge, pts=[c], color=0)
						continue

					# find rectangular bounding
					rect = cv.minAreaRect(c)

					# check aspect ratio, 1.5 aprox. rectangle/square
					(x, y), (w, h), angle = rect
					aspect_ratio = max(w, h) / min(w, h)
					if (aspect_ratio > ASPECT_UPPER) or (aspect_ratio < ASPECT_LOWER):
						cv.fillPoly(edge, pts=[c], color=0)
						continue

					#print(c)
					#if c not null return 1

					# for contours of now correct aspect ratio & greater than 500
					#	create box
					#rect = cv.minAreaRect(c)
					box = cv.boxPoints(rect)
					box = np.int0(box)

					# Calulate Center of Detection
					center = ((box[0][0] + box[3][0])/2, (box[0][1] + box[3][1])/2)

					#return {"Box": box, "Aspect": aspect_ratio, "Center": center}
					img_buf.append({"Box": box, "Aspect": aspect_ratio, "Center": center})
					aspect_sum += aspect_ratio
					count += 1

					# draw detection rectangles
					cv.drawContours(added_img, [box], 0, (0,255,0), 1)

				# display image with detection boxes
				cv.namedWindow('Contours', cv.WINDOW_NORMAL)
				cv.imshow('Contours', added_img)


				if (count >= BUFFER_SIZE):
					avg_aspect = aspect_sum / BUFFER_SIZE
					print(avg_aspect)

					if (avg_aspect <= ASPECT_UPPER) or (avg_aspect >= ASPECT_LOWER):
						return img_buf

					old_data = img_buf.popleft()
					aspect_sum -= old_data["Aspect"] 					
					count -= 1









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

				# on kjey 'q' stop
				if cv.waitKey(1) & 0xFF == ord('q'):
					break

			# destroy them windows
			cv.destroyAllWindows()


detector = Vision()
detection = detector.red_detection()
print("Detection")
print(detection)
