import numpy as np
import cv2
import glob
import camera
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
import picamera
import time
#import json


CALIBRATOR_PARAMS_FILENAME = 'Calibration-Params_Test.txt'

CALIBRATOR_IMAGES_FOLDER = './Chesstest_160x128'


def get_undistort():
	"""Creates a lambda function that takes an image and undistorts it
	after the calibration parameters stored in the dedicated file.
	"""
	calibrator_file = open(CALIBRATOR_PARAMS_FILENAME, 'r')
			
#	mtxL, distL = json.load(calibrator_file)
#	mtx = np.asarray(mtxL)
#	dist = np.asarray(distL)
#	print(dist)
#	print(mtx)

	mtx, dist = eval(''.join(calibrator_file.readlines()).replace('array', ''))
	
	mtx = np.asarray(mtx)
	dist = np.asarray(dist)
	
	calibrator_file.close()
	
	return (lambda img: cv2.undistort(img, mtx, dist, None, mtx))

def create_calibration_images():
	""" Starts a session where the user can use the camera to create
	images to use for calibration. The images will be stored in the
	dedicated folder.
	"""

	#with picamera.PiCamera() as camera:
	camera = picamera.PiCamera()
	camera.resolution = (320,256)
	camera.framerate = 24
	time.sleep(2)

	path = CALIBRATOR_IMAGES_FOLDER

	if not os.path.exists(path):
		os.mkdir(path)
			
	camera.start_preview()

	# Have user take image when pressing enter, end if first typed "end"
	while "end" != input("").lower():
		stream = BytesIO()
		camera.capture(stream, format='jpeg')
		
		# Create image from data
		stream.seek(0)		
		img = Image.open(stream)
		
		# Store image
		now = datetime.now()		
		img.save("{}/CI_{}.jpg".format(path, now.strftime("%y.%m.%d.%H.%M.%S")))



def create_and_save_calibration_params(debug = False):
	""" Goes through each image in the dedicated folder and use them to
	create cailbration params in form of a 3x3 matrix. Uses 
	checkerboard patterns on images.
	
	Use debug=True if the calculations are to be displayed.
	"""
	parameters = calibrate_camera(debug)
	
	mtx = parameters[0]
	
	if debug:
		print(mtx, type(mtx))
		print(mtx[0], type(mtx[0]))
	
	f = open(CALIBRATOR_PARAMS_FILENAME, 'w')
	f.write(str(parameters))
	f.close()


def calibrate_camera(debug = False):
	CHECKERBOARD = (7, 7)

	criteria = (cv2.TERM_CRITERIA_EPS + 
				cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
				
	threedpoints = []

	twodpoints = []

	objectp3d = np.zeros((1, CHECKERBOARD[0]
						  * CHECKERBOARD[1],
						  3), np.float32)
	objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],
								   0:CHECKERBOARD[1]].T.reshape(-1, 2)

	images = glob.glob(f'{CALIBRATOR_IMAGES_FOLDER}/*.jpg')

	if not len(images):
		print("No images found!")
		return None, None

	for filename in images:
		image = cv2.imread(filename)
		grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		ret, corners = cv2.findChessboardCorners(grayColor,
						CHECKERBOARD,
						cv2.CALIB_CB_ADAPTIVE_THRESH
						+ cv2.CALIB_CB_FAST_CHECK +
						cv2.CALIB_CB_NORMALIZE_IMAGE, )
		
		print(filename)

		if ret == True:
			threedpoints.append(objectp3d)
			
			corners2 = cv2.cornerSubPix(
				grayColor, corners, (11, 11), (-1, -1), criteria)
			
			twodpoints.append(corners2)
			
			image = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, ret)
			
		if debug:
			cv2.imshow('img', image)
			cv2.waitKey(0)

#	h, w = image.shape[:2]

	ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
	threedpoints, twodpoints, grayColor.shape[::-1], None, None)
	
	if debug:
		cv2.destroyAllWindows()

		mean_error = 0
		for i in range(len(threedpoints)):
			twodpoints2, _ = cv2.projectPoints(threedpoints[i], r_vecs[i], t_vecs[i], matrix, distortion)
			error = cv2.norm(twodpoints[i], twodpoints2, cv2.NORM_L2)/len(twodpoints2)
			mean_error += error
		print( "Total error: {}".format(mean_error/len(threedpoints)) )

		print(" Camera matrix:")
		print(matrix)
		 
		print("\n Distortion coefficient:")
		print(distortion)
		 
		print("\n Rotation Vectors:")
		print(r_vecs)
		 
		print("\n Translation Vectors:")
		print(t_vecs)
		
	print(matrix, distortion, r_vecs, t_vecs)
		
	return matrix, distortion

if __name__ == "__main__":
	
	#calibrate_camera(1)
	
	create_and_save_calibration_params(True)
	
	#create_calibration_images()
	
