from picamera import PiCamera
from PIL import Image
from io import BytesIO
import cv2

PREFERED_PREVIEW_SIZE = (50,50,500,300)

def create_a_camera():
	camera = PiCamera()
	camera.resolution = (2000,1000)
	camera.framerate = 32
	camera.rotation = 0
	camera.contrast = -40
	camera.hflip = False
	camera.vflip = False
	
	print(camera.brightness)
	
	return camera

def camera_capture_image(camera:PiCamera):
	stream = BytesIO()

	camera.start_preview()
	cam.preview.window = (0,0,500,300)
	cam.preview.fullscreen = False
	# time.sleep(3)
    
	input("")

	camera.capture(stream, format='jpeg')

	# camera.stop_preview()    
    
	stream.seek(0)
	image = Image.open(stream)
    
	return image


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

	test_brightness()

