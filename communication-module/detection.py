import cv2
import numpy as np
from PIL import Image
import camera
import calibrate

TESTFILE =  "CI_22.11.05.00.11.17.jpg"

#DEFAULT_ROI = [(700,0),(0,1000),(2000,1000),(1600,0)]
DEFAULT_ROI = [(700,0),(0,800),(2000,800),(1600,0)]

# ------------------------------------------------
# Display data on image
# ------------------------------------------------

def preview_bitmap_on_image(bitmap, image, color=(0, 255, 0)):
	""" Previews a bitmap overlayed on an image with the provided 
	color.
	"""
	image_to_show = add_bitmap_to_image(bitmap, image, color)
	
	camera.preview_image(final)
	


def add_bitmap_on_image(bitmap, image, color=(0, 255, 0), weight=0.5) -> np.ndarray:
	""" Add a bitmap onto the provided image and return the result. 
	"""
	
	manipulated_image = image.copy()
	
	manipulated_image[bitmap == 1] = np.array(color)
	
	return cv2.addWeighted(manipulated_image, weight, image, 1, 0)


def draw_polynomial_on_image(image:np.ndarray, polynomial, color=(255,255,255)):
	
	plot_over_y = np.linspace(0, image.shape[0]-1, image.shape[0])
	resulting_x = polynomial[0]*plot_over_y**2 + polynomial[1]*plot_over_y + polynomial[2]
	for i in range(len(plot_over_y)):
		cv2.circle(image, (int(resulting_x[i]), int(plot_over_y[i])), 2, [0,255,255], 2)
		
		
def fill_between_polynomials(size, poly1, poly2, debug=True):
	""" Creates a bitmap where the area inbetween the two provided 
	second degree polynomials are filled with ones.
	"""
	
	bitmap = np.empty(size)
	
	# A func that have value be inside of bitmap to avoid incorrect x
	clamp = lambda x: max(min(x, bitmap.shape[1]), 0)

	for y in range(bitmap.shape[0]):
		x1 = clamp(poly1[0] * y**2 + poly1[1] * y + poly1[2])
		x2 = clamp(poly2[0] * y**2 + poly2[1] * y + poly2[2])
		
		x1 = int(x1 + 0.5) # Rounded to closest integer
		x2 = int(x2 + 0.5) # Rounded to closest integer
	
		bitmap[y, min(x1,x2):max(x1,x2)] = 1

	if debug:
		camera.preview_image(bitmap*255)
		
	return bitmap
	


# ------------------------------------------------
# Line detection as a whole
# ------------------------------------------------

def dl_clearify_edges(image:np.ndarray) -> np.ndarray: #just in case we need it
	""" Manipulates provided image to clearify edges. Returns an image 
	with same characteristics.
	"""
	
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)
	
	return blur_image


def get_warp_perspective_funcs(image:np.ndarray, roi=None, target_roi=None, debug=False):
	""" generates a method to warps perspective of an image so that 
	region of interest, roi, covers the target area defined by 
	target_roi. Returns an image with same characteristics.
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
	inv_transform_matrix = cv2.getPerspectiveTransform(target_roi, roi) # Will need for preview
	
	warp_func = lambda img: cv2.warpPerspective(img, transform_matrix, image.shape[::-1][1:] if image.ndim > 2 else image.shape[::-1]) # [1:]) <- Needed for some types of images?!
	warp_back_func = lambda img: cv2.warpPerspective(img, inv_transform_matrix, image.shape[::-1][1:] if image.ndim > 2 else image.shape[::-1]) # [1:]) <- Needed for some types of images?!
	
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
	
	return warp_func, warp_back_func

'''
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)

	sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 7))
	sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 7))
	
	sobel = (sobel_x ** 2 + sobel_y ** 2)**(1/2)

	sobel_image = np.ones_like(sobel, dtype=image.dtype)
	sobel_image[threshold(sobel)] = 0'''

def test_dl_mark_edges(image:np.ndarray, threshold=lambda pix: (pix < 30)):
	""" Returns an image of the provided one where the edges are
	marked.
	"""
	
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)

	sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 7))
	sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 7))
	
	sobel = (sobel_x ** 2 + sobel_y ** 2)**(1/2)

	sobel_image = np.ones_like(sobel, dtype=image.dtype)
	sobel_image[threshold(sobel)] = 0
	
	_, s_binary = cv2.threshold(cvt_image[:,:,2], 70, 255, cv2.THRESH_BINARY_INV)
	_, r_thresh = cv2.threshold(image[:, :, 2], 70, 255, cv2.THRESH_BINARY_INV)
	rs_binary = cv2.bitwise_and(s_binary, r_thresh)
	rs_binary_like = np.ones_like(rs_binary, dtype=image.dtype)
	rs_binary_like[threshold(rs_binary)] = 0 

	sobel_image = cv2.bitwise_or(rs_binary_like, sobel_image.astype(np.uint8))
	
	return sobel_image


def dl_mark_edges(image:np.ndarray, threshold=lambda pix: (pix < 30)):
	""" Returns an image of the provided one where the edges are
	marked.
	"""
	
	cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

	_, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
	
	blur_image = cv2.GaussianBlur(threshed, (7,7), 0)

	sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 7))
	sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 7))
	
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
		camera.preview_image_grid([[pre_image], [graph]])
	
	return lanes[0][0], lanes[1][0]


def detect_lines(image:np.ndarray):
	
	camera.preview_image(image)
	
	undistort = calibrate.get_undistort()

	fisheye_removed = undistort(image)

	warp_func, warp_back_func = get_warp_perspective_funcs(fisheye_removed)
	warped = warp_func(fisheye_removed)
				
	# Does things to image but not warps it
	edges = test_dl_mark_edges(warped)


	lane_left, lane_right = dl_detect_lanes(edges, debug=True)
	
	# Calculate center offset
	camera_pos = image.shape[1]/2 # screen center
	bottom_y = image.shape[0]
	lane_left_at_bottom = lane_left[0] * bottom_y ** 2 + lane_left[1] * bottom_y + lane_left[2]
	lane_right_at_bottom = lane_right[0] * bottom_y ** 2 + lane_right[1] * bottom_y + lane_right[2]	

	center_offset = (lane_left_at_bottom + lane_right_at_bottom)/2 - camera_pos

	# Calculate curvature
	left_curve = ((1 + (2*lane_left[0]*bottom_y + lane_left[1])**2)**1.5) / np.absolute(2*lane_left[0])
	right_curve = ((1 + (2*lane_right[0]*bottom_y + lane_right[1])**2)**1.5) / np.absolute(2*lane_right[0])

	# _________________PREVIEW____________________
	# An image to preview result
	preview_image = undistort(image)	
	
	# Add colored road
	color_these_bits = fill_between_polynomials(image.shape[:2], lane_left, lane_right)
	preview_image = add_bitmap_on_image(warp_back_func(color_these_bits), preview_image, (0,255,0))

	# Add marker for center of road
	cv2.circle(preview_image, (int(camera_pos - center_offset + 0.5), bottom_y), 10, [0,255,255], 18)
	# ____________________________________________
	
	camera.preview_image(preview_image)
		
	
	return center_offset, left_curve, right_curve, preview_image


# ------------------------------------------------
# Testing
# ------------------------------------------------

if __name__ == "__main__":
	
	image = cv2.imread(TESTFILE)	

	center_offset, left_curve, right_curve, pre_image = detect_lines(image)

	# Just so that the final frame is easy to dicern
	cv2.putText(pre_image, "FINAL FRAME", (10,pre_image.shape[0]-100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
	cv2.putText(pre_image, "Center offset: {:.2f}".format(center_offset), (10,pre_image.shape[0]-70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
	cv2.putText(pre_image, "Left curve: {:.2f}".format(left_curve), (10,pre_image.shape[0]-40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
	cv2.putText(pre_image, "Right curve: {:.2f}".format(right_curve), (10,pre_image.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
				
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



