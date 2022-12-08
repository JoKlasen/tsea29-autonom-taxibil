#from picamera import PiCamera
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import time
import time as Time
import os
from datetime import datetime

from typing import Any, Collection, Generator, Tuple
from numbers import Number
from numpy.typing import NDArray

PREFERED_PREVIEW_SIZE = (50,50,1500,800)


# ----- Typing -----
# To make clear relevant data types
# 2D arrays:
ImageMtx = NDArray[np.dtype[np.int8]]
BitmapMtx = NDArray[np.dtype[np.int8]]
TransformMtx = NDArray[np.dtype[np.float64]]
# Simple data:
Pol2d = Tuple[float, float, float]
Vector2d = Tuple[Number, Number]
Color = Collection[int]

# ----------------------------------------------------------------------
# Generic functions 
# ----------------------------------------------------------------------

def create_a_camera() -> 'PiCamera':
	""" Creates a PiCamera object with predefined seetings. 
	
	Note, that most uses of a PiCamera should call this to get it and
	therefore chaning it might have cascading effects.
	"""
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 16
	#   camera.rotation = 0
	camera.contrast = 30
	
	camera.saturation = 0
	camera.sharpness = 0
	
	camera.hflip = False
	camera.vflip = False
	
	return camera
    
    
def get_timestamp() -> str:
    """ Returns tha date and time as a string that can be used in 
    file naming. 
    """
    
    now = datetime.now()
        
    return now.strftime("%y.%m.%d-%H.%M.%S")    


# ----------------------------------------------------------------------
# Take images sessions
# ----------------------------------------------------------------------

    
def create_example_images(path:str = "./Example/"):
	""" Runs a session that will keep loading a folder with images that
	are taken using a new Picamera. 
	"""
	
	cam = create_a_camera()
	
	if not os.path.exists(path):
		os.mkdir(path)
        
	cam.start_preview()
    
	while True:
		# Wait
		time.sleep(5 - time.monotonic() % 1)

		# Take image
		stream = BytesIO()
		cam.capture(stream, format='jpeg')
		stream.seek(0)
        
		img = Image.open(stream)

		# Store image
		now = datetime.now()
		img_name = f"{path}EI_{get_timestamp()}.jpg"
		img.save(img_name)

		print("Image taken: {img_name}")


def camera_capture_image(camera:'PiCamera', debug=False) -> ImageMtx:
	""" Have camera take an image. If debug is True then wait for
	user pressing enter before taking image.
	"""
        
	stream = BytesIO()

	if debug:
		print("start: camera_capture_image")
		camera.start_preview()
		camera.preview.window = (0,0,1000,800)
		camera.preview.fullscreen = False
		input("")
		
		debug_time = Time.time()

    
    # Take image
	camera.capture(stream, format='jpeg')
	stream.seek(0)

	image = Image.open(stream)
    
	if debug:
		debug_time = Time.time() - debug_time

		print("finish: camera_capture_image")
		camera.stop_preview()        
		print("time: ", debug_time)

	return np.asarray(image)

# ----------------------------------------------------------------------
# Preview images
# ----------------------------------------------------------------------

def preview_image(image:ImageMtx, title="¡YEAY!") -> None:
    """ Uses opencv to preview an image """

    # Show window
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 1500, 800)
    cv2.imshow(title, image)

    # Wait on key then destroy
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def preview_image_grid(img_grid:Collection[Collection[ImageMtx]]) -> None:
    """ Uses a grid of images of same size and preview them in one 
    window. 
    """    
    rows = []
    
    # Concatenate images for previewing them
    for img_row in img_grid:
        for i in range(len(img_row)):
            if img_row[i].ndim == 2:
                img_row[i] = np.expand_dims(img_row[i], axis=2)
                img_row[i] = np.concatenate((img_row[i],)*3, axis=2)
                        
        rows.append(np.concatenate(img_row, axis=1))
		
    final = np.concatenate(rows)
    
    # Preview them all
    preview_image(final)
    
    return final


# ----------------------------------------------------------------------
# Test, aspects of Picamera
# ----------------------------------------------------------------------


def test_sharpness():
	""" Test the sharpness attribute of the camera by changing it 
	and previewing the result to the user.
	"""
	
	# A generator that each step sets the sharpness of the camera and 
	# yields its value
	def step_set_sharpness(camera: 'PiCamera'):
		for sharpness in range(-100, 101, 10):
			camera.sharpness = sharpness
			yield sharpness
	
	test_camera_attribute(step_set_sharpness)


def test_saturation():
	""" Test the saturation attribute of the camera by changing it 
	and previewing the result to the user.
	"""
	
	# A generator that each step sets the saturation of the camera and 
	# yields its value
	def step_set_saturation(camera: 'PiCamera'):
		for saturation in range(-100, 101, 10):
			camera.saturation = saturation
			yield saturation
	
	test_camera_attribute(step_set_saturation)


def test_brightness():
	""" Test the brightness attribute of the camera by changing it 
	and previewing the result to the user.
	"""
	
	# A generator that each step sets the brightness of the camera and 
	# yields its value
	def step_set_brightness(camera: 'PiCamera'):
		for brightness in range(0, 101, 10):
			camera.brightness = brightness
			yield brightness
	
	test_camera_attribute(step_set_brightness)


def test_contrast():
	""" Test the contrast attribute of the camera by changing it 
	and previewing the result to the user.
	"""

	# A generator that each step sets the contrast of the camera and 
	# yields its value
	def step_set_contrast(camera: 'PiCamera'):
		for contrast in range(-100, 101, 20):
			camera.contrast = contrast
			yield contrast
	
	test_camera_attribute(step_set_contrast)


def test_awb_mode():
	""" Test the awb_mode attribute of the camera by changing it 
	and previewing the result to the user.
	"""

	# A generator that each step sets the awb_mode of the camera and 
	# yields its value
	def step_set_awb(camera: 'PiCamera'):
		for mode in ['off','sunlight', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']:
			camera.awb_mode = mode
			yield mode
	
	test_camera_attribute(step_set_awb)


def test_camera_attribute(gen:Generator[Any, None, None]):
	""" Test a attribute of the camera by using a generator that steps 
	through camera settings
	"""
		
	# Create camera and wait for it to wake
	camera = create_a_camera()
	time.sleep(3)

	# Iterate through changes and preview
	for state in gen(camera):
		print(f"* {state}", end="")
		
		camera.start_preview()
		camera.preview.window = PREFERED_PREVIEW_SIZE
		camera.preview.fullscreen = False
		
		input("")
		
		camera.stop_preview()
	

# ----------------------------------------------------------------------
# Main, when file is runned
# ----------------------------------------------------------------------


if __name__ == "__main__":

	# test_sharpness()
	
	# test_saturation()
	
	# test_awb_mode()

	# test_contrast()

	test_brightness()

	#camera_capture_image(create_a_camera())
