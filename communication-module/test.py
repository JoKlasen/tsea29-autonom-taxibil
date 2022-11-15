import os
import cv2
from picamera.array import PiRGBArray
from PIL import Image
import time
from calibrate import get_undistort
import numpy as np
from io import BytesIO

import camera
	

def test_calibrated_image():

	cam = camera.create_a_camera()
	undist = get_undistort()	

	cam.start_preview()
	cam.preview.window = (0,0,500,300)
	cam.preview.fullscreen = False


	while input("").lower() != 'end':
		stream = BytesIO()

		cam.capture(stream, format='jpeg')
    
		stream.seek(0)
		image = np.asarray(Image.open(stream))
    
		cal_image = undist(image)
		
		concat_image = np.concatenate((image, cal_image), axis=1)
    
		cam.stop_preview()
    
		im_name = 'NOT CALIBRATED and CALIBRATED'
    
		cv2.namedWindow(im_name, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(im_name, 1500, 1000)
		
		cv2.imshow(im_name, concat_image)
		
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		
		cam.start_preview()
		cam.preview.window = (0,0,500,300)
		cam.preview.fullscreen = False

	cam.stop_preview()

	

if __name__ == '__main__':

	#test_calibrated_image()
	
	cam = camera.create_a_camera()
	undist = get_undistort()	
	
	image = np.array(camera.camera_capture_image(cam))
	undisted = undist(image)
	undistedImage = Image.fromarray(undisted)
	
	undistedImage.show()
	
	undistedImage.save("chess_test.jpg")
	
	
    