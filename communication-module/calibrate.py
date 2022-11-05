import numpy as np
import cv2
import glob
import camera
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
#import json


CALIBRATOR_PARAMS_FILENAME = 'Calibration-Params.txt'


def get_undistort():
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

	cam = camera.create_a_camera()

	path = "./Chesstest/"

	if not os.path.exists(path):
		os.mkdir(path)
			
	cam.start_preview()

	while "end" != input("").lower():
		stream = BytesIO()

		cam.capture(stream, format='jpeg')
		
		stream.seek(0)
		
		img = Image.open(stream)
		
		now = datetime.now()
		
		img.save("{}CI_{}.jpg".format(path, now.strftime("%y.%m.%d.%H.%M.%S")))



def create_and_save_calibration_params():
	parameters = calibrate_camera()
		
	#def rec_convert(l):
		
	#	if len(list) > 0:
	#		result = list()
			
	#		for child in l:
	#			result.append(rec_convert(child))
				
	#	else:
	#		result = l
				
	#	return result
		
	#parameters = rec_convert(parameters)
	
	mtx = parameters[0]
	
	print(mtx, type(mtx))
	print(mtx[0], type(mtx[0]))
	
	f = open(CALIBRATOR_PARAMS_FILENAME, 'w')
	f.write(str(parameters))
	#json.dump(list(parameters), f, indent = 6)
	f.close()


def calibrate_camera(debug = 0):
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

	images = glob.glob('./Chesstest/*.jpg')

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

	h, w = image.shape[:2]

	ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
	threedpoints, twodpoints, grayColor.shape[::-1], None, None)
	
	if debug:
		cv2.destroyAllWindows()

		print(" Camera matrix:")
		print(matrix)
		 
		print("\n Distortion coefficient:")
		print(distortion)
		 
		print("\n Rotation Vectors:")
		print(r_vecs)
		 
		print("\n Translation Vectors:")
		print(t_vecs)
		
	print( ret, matrix, distortion, r_vecs, t_vecs)
		
	return matrix, distortion

if __name__ == "__main__":
	
	#calibrate_camera(1)
	
	#create_and_save_calibration_params()
	
	create_calibration_images()
	
