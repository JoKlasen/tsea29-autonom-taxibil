import cv2
import numpy as np
import time
import os
from PIL import Image
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
# Initialisation
# ----------------------------------------------------------------------

def init(resx:int=320, resy:int=256, fps:int=30) -> cv2.VideoCapture:
    """Initialises a new VideoCapture object with resolution resx, resy 
    that takes fps images per second.
    """

    camera = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,resx)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT,resy)
    camera.set(cv2.CAP_PROP_FPS,fps)
    camera.set(cv2.CAP_PROP_BUFFERSIZE,1)
    camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    camera.set(cv2.CAP_PROP_AUTO_WB, 0)
 
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

def read(cam:cv2.VideoCapture):
    for i in range(3):
        ret = cam.grab()
    return cam.retrieve()

def capture_image(camera:cv2.VideoCapture, debug=False) -> ImageMtx:
    """ Have camera take an image. If debug is True then wait for
    user pressing enter before taking image.
    """
    
    if debug:
        print("start: capture_image")
        debug_time = time.time()
    
    # Take image
    ret, img = read(camera)
    if(not ret):
        print ("Unable to take picture")

    if debug:
        debug_time = time.time() - debug_time
        print("finish: capture_image")
        print("time: ", debug_time)

    return np.asarray(img)


def create_example_images(path:str = "./Example/"):
    """ Runs a session that will keep loading a folder with images that
    are taken using a new VideoCapture. 
    """
    
    cam = init()
    
    if not os.path.exists(path):
        os.mkdir(path)
        
    #cam.start_preview()
    
    while True:
        # Take image
        ret, image = interrupted_preview(cam, wait=5)
        
        if (ret):      
            img = Image.fromarray(image)

            # Store image
            # Store image
            now = datetime.now()        
            img.save("{}/EI_{}.jpg".format(path, now.strftime("%y.%m.%d.%H.%M.%S")))

            print("Image taken: {img_name}")
        else:
            print("Image could not be taken")

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


def interrupted_preview(cam:cv2.VideoCapture, title='Preview', wait:int=0):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 1500, 800)
    ret = False
    img = None
        
    keyPressed = False
    start = time.time()
    while (not keyPressed):
        img = capture_image(cam)
        cv2.imshow(title, img)
        if not cv2.waitKey(40) == -1:
            keyPressed = True
        if wait and time.time() - start > wait:
            break
    cv2.destroyAllWindows()

    return ret, img


# ----------------------------------------------------------------------
# Tests of camera functionality
# ----------------------------------------------------------------------

def test_codec():
    """ Test the codec attribute of the camera by changing it 
    and previewing the result to the user.
    """
    cam = init()
    title = "heh"
    ret, img = cam.read()
    if ret == False:
        print("Failed to take image 1")
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 1500, 800)
    cv2.imshow(title, img)
    # Wait on key then destroy
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('m','j','p','g'))
    ret, img = cam.read()
    if ret == False:
        print("Failed to take image 2")
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 1500, 800)
    cv2.imshow(title, img)
    # Wait on key then destroy
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_brightness():
    """ Test the brightness attribute of the camera by changing it 
    and previewing the result to the user.
    """
    
    # A generator that each step sets the brightness of the camera and 
    # yields its value
    def step_set_brightness(camera: cv2.VideoCapture):
        for brightness in range(0, 101, 10):
            camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
            yield brightness
    
    test_camera_attribute(step_set_brightness)


def test_contrast():
    """ Test the contrast attribute of the camera by changing it 
    and previewing the result to the user.
    """

    # A generator that each step sets the contrast of the camera and 
    # yields its value
    def step_set_contrast(camera: cv2.VideoCapture):
        for contrast in range(-100, 101, 10):
            camera.set(cv2.CAP_PROP_CONTRAST, contrast)
            yield contrast
    
    test_camera_attribute(step_set_contrast)


def test_saturation():
    """ Test the saturation attribute of the camera by changing it 
    and previewing the result to the user.
    """
    
    # A generator that each step sets the saturation of the camera and 
    # yields its value
    def step_set_saturation(camera: cv2.VideoCapture):
        for saturation in range(-100, 101, 10):
            camera.set(cv2.CAP_PROP_SATURATION, saturation)
            yield saturation
    
    test_camera_attribute(step_set_saturation)


def test_sharpness():
    """ Test the sharpness attribute of the camera by changing it 
    and previewing the result to the user.
    """
    
    # A generator that each step sets the sharpness of the camera and 
    # yields its value
    def step_set_sharpness(camera: cv2.VideoCapture):
        for sharpness in range(-100, 101, 10):
            camera.set(cv2.CAP_PROP_SHARPNESS, sharpness)
            yield sharpness
    
    test_camera_attribute(step_set_sharpness)


def test_camera_attribute(gen:Generator[Any, None, None]):
    """ Test a attribute of the camera by using a generator that steps 
    through camera settings
    """
        
    # Create camera
    camera = init()

    # Iterate through changes and preview
    for state in gen(camera):
        print(f"* {state}", end="")
        
        interrupted_preview(camera)

# ----------------------------------------------------------------------
# Main, when file is ran
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # test_codec()

    # test_brightness()

    # test_contrast()

    # test_saturation()

    # test_sharpness()

    interrupted_preview(init(fps=30))
