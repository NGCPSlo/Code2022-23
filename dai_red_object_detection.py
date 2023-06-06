#import the libraries
import cv2 as cv
import numpy as np
import depthai as dai
from collections import deque
import math

# color detection bounds
#HSV_LOW = [160, 100, 50]
#HSV_HIGH = [180, 255, 255]
HSV_LOW = [153, 118, 77]
HSV_HIGH = [255, 255, 255]

# Aspect Ratio Bounds
ASPECT_UPPER = 1.5
ASPECT_LOWER = 0.8
BUFFER_SIZE = 13 # Increasing Buffer improves accuracy, but uses memory

# Physical Constants
MOUNTING_ANGLE = 45 # degrees

# Focal length in pixels (this may need to be calibrated)
# focal length (pixels) = (focal length (mm) / sensor width (mm)) * image width (pixels)
focal_length_pixels = 998


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

		# Define depth output
		stereo = pipeline.create(dai.node.StereoDepth)
		xoutDepth = pipeline.create(dai.node.XLinkOut)
		xoutDepth.setStreamName("depth")

		# Linking
		camRgb.video.link(manip.inputImage)
		manip.out.link(xoutVideo.input)

		stereo.setOutputDepth(True)
		stereo.setOutputRectified(False)
		#0...255 (too high inaccurate, too low more noise)
		stereo.setConfidenceThreshold(155) # determined experimentally

		camMonoLeft = pipeline.create(dai.node.MonoCamera)
		camMonoRight = pipeline.create(dai.node.MonoCamera)
		camMonoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
		camMonoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
		camMonoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
		camMonoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

		# Link the mono cameras to the StereoDepth node
		camMonoLeft.out.link(stereo.left)
		camMonoRight.out.link(stereo.right)

		# Link the depth output
		stereo.depth.link(xoutDepth.input)

		# Properties
		camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
		camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P) #ideally 1080, but 720 for better depth
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
			depth = device.getOutputQueue('depth', maxSize=4, blocking=False)

			img_buf = deque()
			aspect_sum = 0
			depth_sum = 0

			while(True):
				videoFrame = video.get()
				depthFrame = depth.get()
				# reads frames from a camera 
				# ret, img = cap.read()
				img = videoFrame.getCvFrame()
				depthImg = depthFrame.getFrame()

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

					# Get the bounding box in the depth image frame
					x_min = int(min(box, key=lambda x: x[0])[0])
					y_min = int(min(box, key=lambda x: x[1])[1])
					x_max = int(max(box, key=lambda x: x[0])[0])
					y_max = int(max(box, key=lambda x: x[1])[1])
                
					# Get the depth for the bounding box (average)
					boundingBox = depthImg[y_min:y_max, x_min:x_max]
					if boundingBox.size > 0:
						depthBoundingBox = np.average(depthImg[y_min:y_max, x_min:x_max])
						depthBoundingBox = depthBoundingBox / 1000
					else:
						depthBoundingBox = 0
					#print("Depth (in meters):", depthBoundingBox)

					# Calulate Center of Detection
					center = ((box[0][0] + box[3][0])/2, (box[0][1] + box[3][1])/2)

					#return {"Box": box, "Aspect": aspect_ratio, "Center": center}
					img_buf.append({"Box": box, "Aspect": aspect_ratio, "Center": center, "Depth": depthBoundingBox})
					aspect_sum += aspect_ratio
					depth_sum += depthBoundingBox
					count += 1

					# draw detection rectangles
					#cv.drawContours(added_img, [box], 0, (0,255,0), 1)

				# display image with detection boxes
				#cv.namedWindow('Contours', cv.WINDOW_NORMAL)
				#cv.imshow('Contours', added_img)

				#depthImgNormalized = cv.normalize(depthImg, None, 0, 255, cv.NORM_MINMAX)

				# Convert the normalized image to an 8-bit image for displaying
				#depthImgNormalized = np.uint8(depthImgNormalized)

				# Apply the color map to the depth image
				#[depthImgColor = cv.applyColorMap(depthImgNormalized, cv.COLORMAP_JET)


				#cv.namedWindow('depth', cv.WINDOW_NORMAL)
				#cv.imshow('depth', depthImgColor)

				if (count >= BUFFER_SIZE):
					avg_aspect = aspect_sum / BUFFER_SIZE
					avg_depth = depth_sum / BUFFER_SIZE
					#print(avg_aspect)
					#print("Depth")
					#print(avg_depth)

					if (avg_aspect <= ASPECT_UPPER) or (avg_aspect >= ASPECT_LOWER):
						average_box = {"Aspect": 0, "Center": [0,0], "Depth": 0}
						boxes = []
						for i in img_buf:
							boxes.append(i["Box"])
							average_box["Aspect"] += i["Aspect"]
							average_box["Center"][0] += i["Center"][0]
							average_box["Center"][1] += i["Center"][1]
							average_box["Depth"] += i["Depth"]
						
						#print(boxes)
						average_box["Box"] = np.average(boxes, axis = 0)
						average_box["Box"] = np.asarray(average_box["Box"], dtype="int")
						average_box["Aspect"] /= count
						average_box["Center"][0] /= count
						average_box["Center"][1] /= count
						average_box["Depth"] /= count
						#return average_box
						z = math.sin(MOUNTING_ANGLE) * average_box["Depth"]
						y = math.cos(MOUNTING_ANGLE) * average_box["Depth"]

						# Get x coordinates of object's center and image center
						x_centerObject = average_box["Center"][0]
						x_centerImage = added_img.shape[0]/2

						# Compute the horizontal displacement in pixels
						pixel_displacement = x_centerObject - x_centerImage

						# Compute x as the physical displacement in meters
						x = (pixel_displacement / focal_length_pixels) * average_box["Depth"]

						#print(x_center)
						#print([x, y, z])
						return([x, y, z])

					old_data = img_buf.popleft()
					aspect_sum -= old_data["Aspect"] 
					depth_sum -= old_data["Depth"]					
					count -= 1

				# on key 'q' stop
				if cv.waitKey(1) & 0xFF == ord('q'):
					break

			# destroy them windows
			cv.destroyAllWindows()

if __name__ == '__main__':
	detector = Vision()
	detection = detector.red_detection()
	print("Detection")
	print(detection)
