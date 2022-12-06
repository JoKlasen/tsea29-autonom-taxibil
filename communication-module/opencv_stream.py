import cv2
import numpy as np
import time

def init() -> cv2.VideoCapture:
    cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
    #cap = cv2.VideoCapture(-1, 2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,256)
    cap.set(cv2.CAP_PROP_FPS,30)
   
    print("Initialising camera...")
    time.sleep(2)

    if(not(cap.isOpened())):
        print ("Camera was not opened")
    else:
        print ("Camera was opened")

    return cap

def camera_capture_image(camera:cv2.VideoCapture, debug=False):# -> ImageMtx:
	""" Have camera take an image. If debug is True then wait for
	user pressing enter before taking image.
	"""
    
	if debug:
		print("Implement")
        #print("start: camera_capture_image")
		#camera.start_preview()
		#camera.preview.window = (0,0,1000,800)
		#camera.preview.fullscreen = False
		#input("")
		
		#debug_time = Time.time()

    
    # Take image
	ret, img = camera.read()
   
	if debug:
		debug_time = Time.time() - debug_time

		print("finish: camera_capture_image")
		#camera.stop_preview()        
		print("time: ", debug_time)

	return np.asarray(img)



if __name__ == "__main__":
    init()
    #img = None
    start = time.time()
    for i in range(400):
        ret, img = cap.read()
        #print(ret, " , ", img)
    print("Time for 400 frames", time.time()-start)
    
    img.save("./Capture.jpg")
