from picamera import PiCamera
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import time
import os
from datetime import datetime

PREFERED_PREVIEW_SIZE = (50,50,1500,800)

def create_a_camera():
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 16
#	camera.rotation = 0
	camera.contrast = 30
	
	camera.saturation = 0
	camera.sharpness = 0
	
	camera.hflip = False
	camera.vflip = False
	
	return camera
	
def create_example_images():

	cam = create_a_camera()

	path = "./Example/"

	if not os.path.exists(path):
		os.mkdir(path)
			
	cam.start_preview()

	while True:
		time.sleep(5 - time.monotonic() % 1)
		stream = BytesIO()

		cam.capture(stream, format='jpeg')
		
		stream.seek(0)
		
		img = Image.open(stream)
		
		now = datetime.now()
		
		img.save("{}EI_{}.jpg".format(path, now.strftime("%y.%m.%d.%H.%M.%S")))
		print("image taken")

def camera_capture_image(camera:PiCamera, debug=False):
	stream = BytesIO()

	if debug:
		camera.start_preview()
		camera.preview.window = (0,0,1000,800)
		camera.preview.fullscreen = False
		input("")
	# time.sleep(3)
    

	camera.capture(stream, format='jpeg')

	if debug:
		camera.stop_preview()    
    
	stream.seek(0)
	image = Image.open(stream)
    
	return np.asarray(image)


def preview_image(image:np.array, title="¡YEAY!"):

	# Show window
	cv2.namedWindow(title, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(title, 1500, 800)
	cv2.imshow(title, image)

	# Wait on key then destroy
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def preview_image_grid(img_grid):
		
	rows = []
	
	for img_row in img_grid:
		rows.append(np.concatenate(img_row, axis=1))
		
	final = np.concatenate(rows)
	
	preview_image(final)
	
	return final


def test_sharpness():
	camera = create_a_camera()

	camera.stop_preview()

	for contrast in range(-100, 101, 10):
		print(contrast)
		
		camera.sharpness = contrast

		camera.start_preview()
		camera.preview.window = PREFERED_PREVIEW_SIZE
		camera.preview.fullscreen = False
		
		input("")
		
		camera.stop_preview()


def test_saturation():
	camera = create_a_camera()

	for contrast in range(-100, 101, 10):
		print(contrast)
		
		camera.saturation = contrast

		camera.start_preview()
		camera.preview.window = PREFERED_PREVIEW_SIZE
		camera.preview.fullscreen = False
		
		input("")
		
		camera.stop_preview()


def test_brightness():
	camera = create_a_camera()

	for contrast in range(0, 101, 10):
		print(contrast)
		
		camera.contrast = contrast

		camera.start_preview()
		cam.preview.window = PREFERED_PREVIEW_SIZE
		cam.preview.fullscreen = False
		
		input("")
		
		camera.stop_preview()


def test_contrast():
	camera = create_a_camera()

	for contrast in range(-100, 101, 20):
		print(contrast)
		
		camera.contrast = contrast

		camera.start_preview()
		cam.preview.window = PREFERED_PREVIEW_SIZE
		cam.preview.fullscreen = False
		
		input("")
		
		camera.stop_preview()


def test_awb_mode():
	camera = create_a_camera()

	for mode in ['off','sunlight', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']:
		print(mode)
		
		camera.awb_mode = mode

		camera.start_preview()
		cam.preview.window = PREFERED_PREVIEW_SIZE
		cam.preview.fullscreen = False
		
		input("")
		
		camera.stop_preview()


if __name__ == "__main__":
#	test_awb_mode()
#	test_contrast()

#	test_brightness()

	#camera_capture_image(create_a_camera())
	create_example_images()
