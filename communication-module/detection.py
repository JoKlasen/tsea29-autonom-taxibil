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
	""" Previews a bitmap overlayed on an image with the provided 
	color 
	"""
	image_to_show = add_bitmap_to_image(bitmap, image, color)
	
	camera.preview_image(final)
	


def add_bitmap_on_image(bitmap, image, color=(0, 255, 0)) -> np.ndarray:
	
	manipulated_image = image
	
	manipulated_image[bitmap == 1] = np.array(color)
	
	imageArray = cv2.addWeighted(imageArray, 0.5, ori, 1, 0)


def draw_polynomial_on_image(image:np.ndarray, polynomial, color=(255,255,255)):
	
	plot_over_y = np.linspace(0, image.shape[0]-1, image.shape[0])
	resulting_x = polynomial[0]*plot_over_y**2 + polynomial[1]*plot_over_y + polynomial[2]
	for i in range(len(plot_over_y)):
		cv2.circle(image, (int(resulting_x[i]), int(plot_over_y[i])), 2, [0,255,255], 2)


# ------------------------------------------------
# Line detection as a whole
# ------------------------------------------------

def dl_clearify_edges(image:np.ndarray) -> np.ndarray:
	""" Manipulates provided image to clearify edges. Returns an image 
	with same characteristics.
	"""
	
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	# ___Another way to detect edges____
	#	_, s_binary = cv2.threshold(cvt_image[:, :, 2], 110, 255, cv2.THRESH_BINARY_INV)
	#_, r_thresh = cv2.threshold(ori[:,:,2], 70, 255, cv2.THRESH_BINARY)
	#_binary = cv2.bitwise_and(s_binary, r_thresh)

	# ___Another nother way to detect edges____
	#_, s_binary = cv2.threshold(cvt_image[:, :, 2], 110, 255, cv2.THRESH_BINARY_INV)
	#_, r_thresh = cv2.threshold(ori[:,:,2], 70, 255, cv2.THRESH_BINARY)
	#_binary = cv2.bitwise_and(s_binary, r_thresh)
	#mask_maybe = cv2.bitwise_or(_binary, sobel_image.astype(np.uint8))
	
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)
	
	return blur_image


def dl_warp_perspective(image:np.ndarray, roi=None, target_roi=None, debug=False):
	""" Warps perspective of image so that region of interest, roi, 
	covers the target area defined by target_roi. Returns an image with 
	same characteristics.
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
	""" Returns an image of the provided one where the edges are
	marked.
	"""

	sobel_x = np.absolute(cv2.Sobel(image, cv2.CV_64F, 1, 0, 7))
	sobel_y = np.absolute(cv2.Sobel(image, cv2.CV_64F, 0, 1, 7))
	
	sobel = (sobel_x ** 2 + sobel_y ** 2)**(1/2)

	sobel_image = np.ones_like(sobel, dtype=image.dtype)
	sobel_image[threshold(sobel)] = 0

	return sobel_image
	

def dl_detect_lanes(image:np.ndarray, numb_windows = 20, lane_margin=100, min_to_recenter_window=10, debug = False):
	"""	Takes an bitmap and returns lanes tracked on it """
	 
	# Find where pixels are concentrated
	distrubution = np.sum(
		image[:,:], 	# Check whole image
#		image[:int(image.shape[0]/2),:],	# Below half image
#		image[int(image.shape[0]/2):,:], 	# Above half image
		axis=0
	)
	
	mid = int(distrubution.shape[0]/2)
	# Have lanes start at highest peek on each side of the image
	left_lane_start = np.argmax(distrubution[:mid])
	right_lane_start = np.argmax(distrubution[mid:]) + mid
	
	# ----------DEBUG-----------
	if debug:
		pre_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2RGB)
		
		# Fill histogram with pixels after distrubution and fill
		# left_lane_start and right_lane_start with blue pixels
		graph = np.zeros_like(pre_image)
		for x in range(len(distrubution)):
			for y in range(distrubution[x]):
				if x == left_lane_start or x == right_lane_start:
					graph[y][x] = np.asarray((255,0,0), dtype=graph.dtype)
				else:
					graph[y][x] = np.asarray((255,255,255), dtype=graph.dtype)
						
		# Write out location of left_lane_start and right_lane_start
		cv2.putText(graph, "LEFT LANE PEEK: " + str(left_lane_start), (10,graph.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
		cv2.putText(graph, "RIGHT LANE PEEK: " + str(right_lane_start), (10,graph.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))

		# camera.preview_image_grid([[pre_image],[graph]])
	# --------------------------
	
	# Use sliding window technique to track lanes
	window_height = int(image.shape[0]/numb_windows)
	lanes = ([left_lane_start], [right_lane_start])
	
	if debug:
		pre_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2RGB)
	
	for lane_package in lanes:
		
		current_x = lane_package[0]
		lane_pixels = [
			np.empty(0),
			np.empty(0)
		]
		
		for win_i in range(numb_windows):
		
			win_x = (
				current_x - lane_margin,
				current_x + lane_margin,
			)
			win_y = (
				image.shape[0] - (win_i + 1) * window_height,
				image.shape[0] - win_i * window_height
			)
						
			# Find pixels in window	
			pixels_in_window = (image[win_y[0]:win_y[1], win_x[0]:win_x[1]]).nonzero()
										
			# Remember pixels for the lane
			lane_pixels[0] = np.append(lane_pixels[0], pixels_in_window[1] + win_x[0])
			lane_pixels[1] = np.append(lane_pixels[1], pixels_in_window[0] + win_y[0])
			
			if len(pixels_in_window[0]) > min_to_recenter_window:
				# Recenter around found pixels
				current_x = int(np.mean(pixels_in_window[1])) + win_x[0]
	
			if debug:
				# Displays where the window were when finding the pixels
				cv2.rectangle(pre_image,(win_x[0], win_y[0]),(win_x[1], win_y[1]), (255,255,255), 2)
				# Displays where the window is after moving it
				# cv2.rectangle(pre_image,(current_x - lane_margin, win_y[0]),(current_x + lane_margin, win_y[1]), (255,0,0), 2)

		# Calculate parameters		
		polynomial = np.polyfit(lane_pixels[1], lane_pixels[0], 2)

		# Store found values
		lane_package[0] = polynomial
		
		if debug:
			# Fill pixels used to calculate line
			pre_image[lane_pixels[1].astype(int), lane_pixels[0].astype(int)] = [0, 255, 0] if np.array_equal(lanes[0], lane_package) else [0,0,255]
			
			
			
			# Draw calculated line on image
			draw_polynomial_on_image(pre_image, polynomial, [0, 255, 255])
			
							
	if debug:
		camera.preview_image(pre_image)
	
	return lanes[0], lanes[1]


def detect_lines(image:np.ndarray):
	
	manipulated = dl_clearify_edges(image)

	#camera.preview_image(manipulated)

	fisheye_removed = calibrate.get_undistort()(manipulated)

	#camera.preview_image(fisheye_removed)

	warped = dl_warp_perspective(fisheye_removed)

	#camera.preview_image(warped)
		
	edges = dl_mark_edges(warped)

	# camera.preview_image(edges*255)

	lane1, lane2 = dl_detect_lanes(edges, debug=True)
	


	# An image to preview result
	preview_image = edges

	# Edges found
	param1 = lane1
	param2 = lane2
	param3 = None

	#preview_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB) * 255
	
	return param1, param2, param3, preview_image


# ------------------------------------------------
# Testing
# ------------------------------------------------d

if __name__ == "__main__":
	
	image = cv2.imread(TESTFILE)	

	param1, param2, param3, pre_image = detect_lines(image)

	print(param1, param2)

	# Just so that the final frame is easy to dicern
	cv2.putText(pre_image, "FINAL FRAME", (10,pre_image.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
				
				
	camera.preview_image(pre_image, "FINAL FRAME")

		
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



