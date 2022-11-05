import cv2
import numpy as np
from PIL import Image
import camera
import calibrate

TESTFILE =  "CI_22.11.05.00.11.17.jpg"

DEFAULT_ROI = [(700,0),(0,800),(2000,800),(1600,0)]


# ------------------------------------------------
# Display data on image
# ------------------------------------------------

def preview_bitmap_on_image(bitmap, image, color=(0, 255, 0)):
	
	image_to_show = add_bitmap_to_image(bitmap, image, color)
	
	camera.preview_image(final)
	


def add_bitmap_on_image(bitmap, image, color=(0, 255, 0)) -> np.ndarray:
	manipulated_image = image
	
	manipulated_image[bitmap == 1] = np.array(color)
	
	imageArray = cv2.addWeighted(imageArray, 0.5, ori, 1, 0)


# ------------------------------------------------
# Line detection as a whole
# ------------------------------------------------

def dl_clearify_edges(image:np.ndarray) -> np.ndarray:
	"""
	Manipulates provided image to clearify edges. Returns an image with 
	same characteristics.
	"""
	
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)
	
	return blur_image


def dl_warp_perspective(image:np.ndarray, roi=None, target_roi=None, debug=False):
	"""
	Warps perspective of image so that region of interest, roi, covers
	the target area defined by target_roi. Returns an image with same
	characteristics.
	"""

	if roi == None:
		roi = DEFAULT_ROI
	roi = np.float32(roi)

	if target_roi == None:
		target_roi = [
			(0, 				0),					# Top-left
			(0, 				image.shape[0]),	# Bottom-left
			(image.shape[1], 	image.shape[0]),	# Bottom-right
			(image.shape[1], 	0)					# Top-right
		]
	target_roi = np.float32(target_roi)

	transform_matrix = cv2.getPerspectiveTransform(roi, target_roi)
	# inv_transform_matrix = cv2.getPerspectiveTransform(target_roi, roi) # Will need for preview
	
	warped = cv2.warpPerspective(image, transform_matrix, image.shape[::-1]) # [1:]) <- Needed for some types of images?!
	
	# ----------DEBUG-----------
	if debug:
		warped_preview = warped.copy()
		for point in np.int32(target_roi):
			cv2.circle(warped_preview, point, 10, (0,0,255), cv2.FILLED)

		image_preview = image.copy()
		for point in np.int32(roi):
			cv2.circle(image_preview, point, 10, (255,0,0), cv2.FILLED)

		cv2.polylines(image_preview, np.int32([roi]), True, (255,0,0), 2)
		
		camera.preview_image_grid([[image_preview, warped_preview]])
	# --------------------------
	
	return warped


def dl_mark_edges(image:np.ndarray, threshold=lambda pix: (pix < 30)):

	sobel_x = np.absolute(cv2.Sobel(image, cv2.CV_64F, 1, 0, 7))
	sobel_y = np.absolute(cv2.Sobel(image, cv2.CV_64F, 0, 1, 7))
	
	sobel = (sobel_x ** 2 + sobel_y ** 2)**(1/2)

	sobel_image = np.ones_like(sobel, dtype=image.dtype)
	sobel_image[threshold(sobel)] = 0

	return sobel_image
	

""" 
TEST
	
def dl_mark_edges(image:np.ndarray, threshold=lambda pix: (sobel >= 110) & (sobel <= 255)):

	_, s_binary = cv2.threshold(cvt_image[:, :, 2], 110, 255, cv2.THRESH_BINARY_INV)
	_, r_thresh = cv2.threshold(ori[:,:,2], 70, 255, cv2.THRESH_BINARY)
	_binary = cv2.bitwise_and(s_binary, r_thresh)
	blur_image = cv2.GaussianBlur(_binary, (7,7), 0)
	sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 3))
	sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 3))
	sobel = (sobel_x ** 2 + sobel_y ** 2)**1/2
	sobel_image = np.ones_like(sobel, dtype=blur_image.dtype)
	sobel_image[] = 0

	return sobel
"""

"""
def dl_mark_edges(image:np.ndarray, threshold=lambda pix: (sobel >= 110) & (sobel <= 255)):
	_, s_binary = cv2.threshold(cvt_image[:, :, 2], 110, 255, cv2.THRESH_BINARY_INV)
	_, r_thresh = cv2.threshold(ori[:,:,2], 70, 255, cv2.THRESH_BINARY)
	_binary = cv2.bitwise_and(s_binary, r_thresh)
	mask_maybe = cv2.bitwise_or(_binary, sobel_image.astype(np.uint8))

	return sobel	
"""


def detect_lines(image:np.ndarray):
	
	manipulated = dl_clearify_edges(image)

	camera.preview_image(manipulated)

	fisheye_removed = calibrate.get_undistort()(manipulated)

	camera.preview_image(fisheye_removed)

	warped = dl_warp_perspective(fisheye_removed)

	camera.preview_image(warped)
		
	edges = dl_mark_edges(warped)

	camera.preview_image(edges*255)

	lane1, lane2 = None, None # Detect lanes

	# Edges found
	param1 = None
	param2 = None
	param3 = None

	preview_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB) * 255
	
	return param1, param2, param3, preview_image


# ------------------------------------------------
# Testing
# ------------------------------------------------

if __name__ == "__main__":
	
	image = cv2.imread(TESTFILE)	

	_, _, _, pre_image = detect_lines(image)

	# Just so that the final frame is easy to dicern
	cv2.putText(pre_image, "FINAL FRAME", (10,pre_image.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
				
#	camera.preview_image(pre_image, "FINAL FRAME")

		
	#print(cv2.threshold(cvt_image[:,:,1], 130, 255, cv2.THRESH_BINARY_INV))

	# threshold = 50
	#h_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,0], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
	#l_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,1], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
	#s_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,2], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)

	"""
	# --- PRINT HLS images as well ---
	
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	h_img = cv2.cvtColor(cvt_image[:,:,0], cv2.COLOR_GRAY2RGB)
	l_img = cv2.cvtColor(cvt_image[:,:,1], cv2.COLOR_GRAY2RGB)
	s_img = cv2.cvtColor(cvt_image[:,:,2], cv2.COLOR_GRAY2RGB)

	camera.preview_image_grid([
		[h_img, l_img],
		[s_img, pre_image]
	])
	"""



