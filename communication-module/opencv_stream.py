import cv2
import numpy as np
import time

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

def init(resx:int=320, resy:int=256, fps:int=30) -> cv2.VideoCapture:
    """Initialises a new VideoCapture object with resolution resx, resy 
    that takes fps images per second.
    """

    camera = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,resx)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT,resy)
    camera.set(cv2.CAP_PROP_FPS,fps)

    print("Initialising camera...")
    time.sleep(2)

    ret, img = camera.read()
    if(not(camera.isOpened() and ret)):
        print ("Camera was not opened")
    else:
        print ("Camera was opened")

    return camera

# ----------------------------------------------------------------------
# Take images sessions
# ----------------------------------------------------------------------

def camera_capture_image(camera:cv2.VideoCapture, debug=False):# -> ImageMtx:
	""" Have camera take an image. If debug is True then wait for
	user pressing enter before taking image.
	"""
    
	if debug:
		print("start: camera_capture_image")
		#camera.start_preview()
		#camera.preview.window = (0,0,1000,800)
		#camera.preview.fullscreen = False
		#input("")		
		debug_time = time.time()

    # Take image
	ret, img = camera.read()
   
	if debug:
		debug_time = time.time() - debug_time
		print("finish: camera_capture_image")
		#camera.stop_preview()        
		print("time: ", debug_time)

	return np.asarray(img)


def create_example_images(path:str = "./Example/"):
	""" Runs a session that will keep loading a folder with images that
	are taken using a new Picamera. 
	"""
	
	cam = init(320,256,60)
	
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

def live_preview():
    """ Uses opencv to preview an image """

    # Show window
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 1500, 800)
    cv2.imshow(title, image)
    print("TODO!!!!")

# ----------------------------------------------------------------------
# Tests of camera functionality
# ----------------------------------------------------------------------

def test_images():
    cam = init()
    
    ret, img = cam.read()
    if ret == False:
        print("Failed to take image 1")
    img.save("./Capture_normal.png")
    
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('m','j','p','g'))
    ret, img = cam.read()
    if ret == False:
        print("Failed to take image 2")
    img.save("./Capture_mjpeg.png")

    #cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('m','j','p','g'))
    #ret, img = cam.read()
    #if ret == False:
    #    print("Failed to take image 2")
    #img.save("./Capture_mjpeg.png")

    #cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('m','j','p','g'))
    #ret, img = cam.read()
    #if ret == False:
    #    print("Failed to take image 2")
    #img.save("./Capture_mjpeg.png")
    

# ----------------------------------------------------------------------
# Main, when file is ran
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # test_sharpness()
	
	# test_saturation()
	
	# test_awb_mode()

	# test_contrast()

	# test_brightness()

    test_images()
