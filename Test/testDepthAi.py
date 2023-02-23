import cv2
import depthai as dai

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

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    video = device.getOutputQueue('video')
    i = 0
    while True:
        videoFrame = video.get()
        # Get BGR frame from NV12 encoded video frame to show with opencv
        cv2.imshow("video", videoFrame.getCvFrame())
        
        if cv2.waitKey(1) == ord('k'):
            
            cv2.imwrite("image"+str(i)+".png", videoFrame.getCvFrame())
            i+=1
        if cv2.waitKey(1) == ord('q'):
            break
