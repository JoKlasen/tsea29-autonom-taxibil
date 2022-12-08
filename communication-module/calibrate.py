import numpy as np
import cv2
import glob
import opencv_stream as camera
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
import time

from typing import Tuple, Callable, Any
from camera import ImageMtx, TransformMtx
from numpy.typing import NDArray


# ----- Parameters -----
# Change as required
CALIBRATOR_PARAMS_FILENAME = 'Calibration-Params_Test.txt'
CALIBRATOR_IMAGES_FOLDER = './Chesstest_160x128'


def get_undistort() -> Callable[[ImageMtx], ImageMtx]:
	"""Creates a lambda function that takes an image and undistorts it
	after the calibration parameters stored in the dedicated file.
	"""
	
	# Get paramters from file
	calibrator_file = open(CALIBRATOR_PARAMS_FILENAME, 'r')
	mtx, dist = eval(''.join(calibrator_file.readlines()).replace('array', ''))
	
	mtx = np.asarray(mtx)
	dist = np.asarray(dist)
	
	calibrator_file.close()
	
	# Return a lambda that is just cv2.undistort but with parameters
	# already inserted
	return (lambda img: cv2.undistort(img, mtx, dist, None, mtx))
	

def create_calibration_images() -> None:
	""" Starts a session where the user can use the camera to create
	images to use for calibration. The images will be stored in the
	dedicated folder.
	"""
	
	# Initialises camera
	cam = camera.init(320,256,24)

	# Wait for camera to wake (or images will have bad lighting)
	time.sleep(2)

	# Load folder
	path = CALIBRATOR_IMAGES_FOLDER
	if not os.path.exists(path):
		os.mkdir(path)

	# Have user take image when pressing enter, end if first typed "end"
	while ("end" != input("").lower()):
        ret, image = camera.interrupted_preview(cam)
		if ret:
            img = Image.open(image)
            
            # Store image
            now = datetime.now()		
            img.save("{}/CI_{}.jpg".format(path, now.strftime("%y.%m.%d.%H.%M.%S")))
        else:
            print("Calibrate: Failed to capture image")


def create_and_save_calibration_params(debug = False) -> None:
	""" Goes through each image in the dedicated folder and use them to
	create cailbration params in form of a 3x3 matrix. Uses 
	checkerboard patterns on images. The result is stored in the 
	CALIBRATOR_PARAMS_FILENAME file.
	
	Use debug=True if the calculations are to be displayed.
	"""

	parameters = calibrate_camera(debug)
	
	mtx = parameters[0]
	
	if debug:
		print("___Result:___")
		print(mtx, type(mtx))
	
	# Store result
	f = open(CALIBRATOR_PARAMS_FILENAME, 'w')
	f.write(str(parameters))
	f.close()


def calibrate_camera(debug = False, checkerboard = (7, 7)) -> Tuple[TransformMtx, NDArray[np.dtype[np.float64]]]:
	""" Creates the parameters from the images in the folder
	CALIBRATOR_IMAGES_FOLDER and stores them in the file
	CALIBRATOR_PARAMS_FILENAME. 
	"""

	# Setup
	criteria = (cv2.TERM_CRITERIA_EPS + 
				cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
				
	threedpoints = []
	twodpoints = []

	objectp3d = np.zeros((1, checkerboard[0]
						  * checkerboard[1],
						  3), np.float32)
	objectp3d[0, :, :2] = np.mgrid[0:checkerboard[0],
								   0:checkerboard[1]].T.reshape(-1, 2)

	# Load images
	images = glob.glob(f'{CALIBRATOR_IMAGES_FOLDER}/*.jpg')
	if not len(images):
		print("No images found!")
		return None, None

	# For each image, find corners and interprit translation required
	# to straighten them
	for filename in images:
		image = cv2.imread(filename)
		grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		ret, corners = cv2.findChessboardCorners(grayColor,
						checkerboard,
						cv2.CALIB_CB_ADAPTIVE_THRESH
						+ cv2.CALIB_CB_FAST_CHECK +
						cv2.CALIB_CB_NORMALIZE_IMAGE, )
		
		if ret == True:
			threedpoints.append(objectp3d)
			
			corners2 = cv2.cornerSubPix(
				grayColor, corners, (11, 11), (-1, -1), criteria)
			
			twodpoints.append(corners2)
			
			image = cv2.drawChessboardCorners(image, checkerboard, corners2, ret)
			
		if debug:
			print(filename)
			cv2.imshow('img', image)
			cv2.waitKey(0)

	# Actually get calibration parameters using opencv 
	ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
	threedpoints, twodpoints, grayColor.shape[::-1], None, None)
	
	if debug:
		cv2.destroyAllWindows()

		# Calculate the error of the transform
		mean_error = 0
		for i in range(len(threedpoints)):
			twodpoints2, _ = cv2.projectPoints(threedpoints[i], r_vecs[i], t_vecs[i], matrix, distortion)
			error = cv2.norm(twodpoints[i], twodpoints2, cv2.NORM_L2)/len(twodpoints2)
			mean_error += error

		# Print result
		print(f"*** Total error: {mean_error/len(threedpoints)}")
		print("Note: Lower value should mean better transform \n")

		print(f"*** Camera matrix: \n{matrix}")
		print(f"*** Distortion coefficient: \n{distortion}")	 
		print(f"*** Rotation Vectors: \n{r_vecs}")
		print(f"*** Translation Vectors: \n{t_vecs}")
			
	return matrix, distortion

if __name__ == "__main__":
	
	calibrate_camera(1)
	
	#create_and_save_calibration_params(True)
	
	#print("LOADED!")
	
	#create_calibration_images()
	
