import cv2
import numpy as np
from PIL import Image
import camera
import calibrate
import math
import time as Time

from typing import Tuple
from camera import ImageMtx, BitmapMtx, Poly2d, Vector2d, Color

TESTFILE =  "CI_22.11.05.00.11.17.jpg"

# ----- Parameters -----
# Change as required
#DEFAULT_ROI = [(700,0),(0,1000),(2000,1000),(1600,0)] # 2000x1000
#DEFAULT_ROI = [(0,180),(0,440),(640,440),(640,180)] # 640x480 180 was 130 changed offset of above part to 0
DEFAULT_ROI = [(0,110),(0,256),(320,256),(320,110)] #320x256


# ----------------------------------------------------------------------
# Display data on image
# ----------------------------------------------------------------------

def preview_bitmap_on_image(bitmap: BitmapMtx, image: ImageMtx, color:Color=(0, 255, 0)) -> None:
    """ Previews a bitmap overlayed on an image with the provided 
    color.
    """

    # ~ print("start: preview_bitmap_on_image")
    # ~ debug_time = Time.time()

    image_to_show = add_bitmap_to_image(bitmap, image, color)
    
    camera.preview_image(final)

    # ~ print("finish: preview_bitmap_on_image")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("time: ", debug_time)
    


def add_bitmap_on_image(
	bitmap: BitmapMtx, image: ImageMtx, 
	color:Color=(0, 255, 0), weight=0.5
	) -> ImageMtx:
    """ Add a bitmap onto the provided image and return the result. 
    """

    # ~ print("start: add_bitmap_on_image")
    # ~ debug_time = Time.time()
    
    manipulated_image = image.copy()
    
    manipulated_image[bitmap == 1] = np.array(color)

    # ~ print("finish: add_bitmap_on_image")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("time: ", debug_time)
    
    return cv2.addWeighted(manipulated_image, weight, image, 1, 0)


def draw_polynomial_on_image(image:ImageMtx, polynomial:Poly2d, color:Color=(255,255,255)) -> None:
	""" Draws the provided second degree polynomial on the image. Image
	will be changed, not returning anything.
	"""
	# ~ print("start: draw_polynomial_on_image")
	# ~ debug_time = Time.time()
    
	plot_over_y = np.linspace(0, image.shape[0]-1, image.shape[0])
	resulting_x = polynomial[0]*plot_over_y**2 + polynomial[1]*plot_over_y + polynomial[2]
	for i in range(len(plot_over_y)):
		cv2.circle(image, (int(resulting_x[i]), int(plot_over_y[i])), 2, [0,255,255], 2)

	# ~ print("finish: draw_polynomial_on_image")
	# ~ debug_time = Time.time() - debug_time
	# ~ print("time: ", debug_time)
        
        
def fill_between_polynomials(size:Vector2d, poly1:Poly2d, poly2:Poly2d, debug=False) -> BitmapMtx:
    """ Creates a bitmap where the area inbetween the two provided 
    second degree polynomials are filled with ones.
    """
    
    # ~ print("start: fill_between_polynomials")
    # ~ debug_time = Time.time()

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
        
    # ~ print("finish: fill_between_polynomials")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("time: ", debug_time)

    return bitmap


# ----------------------------------------------------------------------
# Calculate errors
# ----------------------------------------------------------------------


def calc_adjust_turn(
	left_lane:Poly2d, right_lane:Poly2d, 
	camera_pos, hit_height= 100
) -> Tuple[float, float, Vector2d, Vector2d]:
    """ left_lane and right_lane is a 2nd degree polynomial. 
    camera_pos = (x,y) 
    """
    
    # ~ print("start: calc_adjust_turn")
    # ~ debug_time = Time.time()

    if left_lane is None and right_lane is None:
    
        return 0, 0
    
    else:
        # Flip x, y axises cause mixed
        hit_x = hit_height
            
        # Calculate lane to follow
        if right_lane is None:
            hit_x += int(left_lane[0]*camera_pos[0]**2 + left_lane[1]*camera_pos[0]+left_lane[2])
            lane = np.asarray(left_lane) 
        elif left_lane is None:
            hit_x -= int(right_lane[0]*camera_pos[0]**2 + right_lane[1]*camera_pos[0]+right_lane[2])
            lane = np.asarray(right_lane) 
        else:
            lane = np.asarray([(left_lane[i] + right_lane[i]) / 2 for i in range(3)])
        
        hit_y = lane[0] * hit_x ** 2 + lane[1] * hit_x + lane[2]
                
        hit_vector = (hit_x - camera_pos[0], hit_y - camera_pos[1])
        # Rotate so 0 is straight forward
        hit_vector = (hit_vector[1], -hit_vector[0])

        turn_to_hit = math.atan2(hit_vector[0], hit_vector[1])  
        
        align_slope = 2*lane[0]*hit_x + lane[1]
        align_vector = (1, align_slope)
        # Rotate so 0 is straight forward
        align_vector = (-align_vector[1], align_vector[0])

        turn_to_align = math.atan2(align_vector[0], align_vector[1])
        
        # ~ print("finish: calc_adjust_turn")
        # ~ debug_time = Time.time() - debug_time
        # ~ print("time: ", debug_time)
        
        return turn_to_hit, turn_to_align, (hit_x, hit_y), align_vector


def calc_error(turn_hit, turn_align, turnconst=1, alignconst=1, debug=False):
    """ 
    """
        
    # ~ print("start: calc_error")
    # ~ debug_time = Time.time()

    error = turn_hit*turnconst + turn_align*alignconst #feel free to remove if it doesn't work
    print(error)
    if -0.13 < error < 0.13:
        error = 0

    if debug:
        print(f"""
        ___________________________
        Turn to hit:  {turn_hit} (x{turnconst})
        Turn to align {turn_align} (x{alignconst})
        Error:        {error}
        """)

    # ~ print("finish: calc_error")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("time: ", debug_time)

    return error

# ----------------------------------------------------------------------
# Line detection as a whole
# ----------------------------------------------------------------------

def dl_clearify_edges(image:ImageMtx) -> ImageMtx: #just in case we need it
    """ Manipulates provided image to clearify edges. Returns an image 
    with same characteristics.
    """

    # ~ print("start: dl_clearify_edges")
    # ~ debug_time = Time.time()
    
    cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

    _, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
    
    
    blur_image = cv2.GaussianBlur(threshed, (7,7), 0)
    
    # ~ print("finish: dl_clearing_edges")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("time: ", debug_time)

    return blur_image


def get_warp_perspective_funcs(image:ImageMtx, roi=None, target_roi=None, debug=False) -> ImageMtx:
    """ generates a method to warps perspective of an image so that 
    region of interest, roi, covers the target area defined by 
    target_roi. Returns an image with same characteristics.
    """

    # ~ print("start: get_warp_perspective_funcs")
    # ~ debug_time = Time.time()

    if roi == None:
        roi = DEFAULT_ROI
    roi = np.float32(roi)

    if target_roi == None:
        target_roi = [
            (0,                 0),                 # Top-left
            (0,                 image.shape[0]),    # Bottom-left
            (image.shape[1],    image.shape[0]),    # Bottom-right
            (image.shape[1],    0)                  # Top-right
        ]
    target_roi = np.float32(target_roi)

    transform_matrix = cv2.getPerspectiveTransform(roi, target_roi)
    inv_transform_matrix = cv2.getPerspectiveTransform(target_roi, roi) # Will need for preview
    
    warp_func = lambda img: cv2.warpPerspective(img, transform_matrix, image.shape[::-1][1:] if image.ndim > 2 else image.shape[::-1]) # [1:]) <- Needed for some types of images?!
    warp_back_func = lambda img: cv2.warpPerspective(img, inv_transform_matrix, image.shape[::-1][1:] if image.ndim > 2 else image.shape[::-1]) # [1:]) <- Needed for some types of images?!
    
    # ----------DEBUG-----------
    if debug:
        warped = warp_func(image)
        
        warped_preview = warped.copy()
        for point in np.int32(target_roi):
            cv2.circle(warped_preview, point, 10, (0,0,255), cv2.FILLED)

        image_preview = image.copy()
        for point in np.int32(roi):
            cv2.circle(image_preview, point, 10, (255,0,0), cv2.FILLED)

        cv2.polylines(image_preview, np.int32([roi]), True, (255,0,0), 2)
        
        camera.preview_image_grid([[image_preview, warped_preview]])
    # --------------------------

    # ~ print("finish: get_warp_perspective_funcs")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("time: ", debug_time)
    
    return warp_func, warp_back_func

def dl_mark_edges(image:ImageMtx, threshold=lambda pix: (pix < 30)) -> ImageMtx:
    """ Returns an image of the provided one where the edges are
    marked.
    """

    print("start: dl_mark_edges")
    debug_time = Time.time()
    
    cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

    _, threshed = cv2.threshold(cvt_image[:,:,1], 60, 255, cv2.THRESH_BINARY_INV)
    
    blur_image = cv2.GaussianBlur(threshed, (7,7), 0)

    sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, 7))
    sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, 7))
    
    sobel = np.sqrt(np.square(sobel_x ** 2) + np.square(sobel_y ** 2)) 
    #sobel = (sobel_x ** 2 + sobel_y ** 2)**(1/2)

    sobel_image = np.ones_like(sobel, dtype=image.dtype)
    sobel_image[threshold(sobel)] = 0
    
    # ~ _, s_binary = cv2.threshold(cvt_image[:,:,2], 70, 255, cv2.THRESH_BINARY_INV)
    # ~ _, r_thresh = cv2.threshold(image[:, :, 2], 70, 255, cv2.THRESH_BINARY_INV)
    # ~ rs_binary = cv2.bitwise_and(s_binary, r_thresh)
    # ~ rs_binary_like = np.ones_like(rs_binary, dtype=image.dtype)
    # ~ rs_binary_like[threshold(rs_binary)] = 0 

    # ~ sobel_image = cv2.bitwise_or(rs_binary_like, sobel_image.astype(np.uint8))
    
    print("finish: dl_mark_edges")
    debug_time = Time.time() - debug_time
    print("time: ", debug_time)

    return sobel_image


def dl_detect_lanes(
	image:ImageMtx, 
	numb_windows=20, lane_margin=50, min_to_recenter_window=10, 
	debug=False, get_pics=False
) -> Tuple[Poly2d, Poly2d, ImageMtx, ImageMtx]:
	""" Takes an bitmap and returns lanes tracked on it """
     
	print("start: dl_detect_lanes")
	debug_time = Time.time()

	# Find where pixels are concentrated
	distrubution = np.sum(
#       image[:,:],     # Check whole image
#       image[:int(image.shape[0]/2),:],    # Above half image
		image[int(image.shape[0]/2):,:],    # Below half image
		axis=0
	)

	mid = int(distrubution.shape[0]/2)
    # Have lanes start at highest peek on each side of the image
	left_lane_start = np.argmax(distrubution[:mid])
	right_lane_start = np.argmax(distrubution[mid:]) + mid

	if right_lane_start == mid:
		right_lane_start = distrubution.shape[0]-1
    
    # ----------DEBUG-----------
	if debug or get_pics:
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
    
	if debug or get_pics:
		pre_image = cv2.cvtColor(image*255, cv2.COLOR_GRAY2RGB)

	for lane_package in lanes:

		current_x = lane_package[0]
		lane_pixels = [
			np.empty(0),
			np.empty(0)
		]
        
		for win_i in range(numb_windows):
        
			win_x = (
				max(0, current_x - lane_margin),
				min(image.shape[1], current_x + lane_margin)
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
    
			if debug or get_pics:
				# Displays where the window were when finding the pixels
				cv2.rectangle(pre_image,(win_x[0], win_y[0]),(win_x[1], win_y[1]), (255,255,255), 2)


		if len(lane_pixels[1]) > 0:
			# Calculate parameters      
			polynomial = np.polyfit(lane_pixels[1], lane_pixels[0], 2)
			# Store found values
			lane_package[0] = polynomial
                    
			if debug or get_pics:
				# Fill pixels used to calculate line
				pre_image[lane_pixels[1].astype(int), lane_pixels[0].astype(int)] = [0, 255, 0] if np.array_equal(lanes[0], lane_package) else [0,0,255]

				# Draw calculated line on image
				draw_polynomial_on_image(pre_image, polynomial, [0, 255, 255])

		else:
			# Store bad value since no points found
			lane_package[0] = None

	special_rect = image[int(image.shape[0]/2):int(image.shape[0]/2 + image.shape[0]/4) ,int(image.shape[1]/4):int(image.shape[1] - image.shape[1]/4)]
	special_distr = np.sum(special_rect)
	intersection = False
	right_stop = False
	left_stop = False
	if special_distr > 200:
		left_side = np.sum(special_rect[:,:int(special_rect.shape[1]/2)])
		right_side =np.sum(special_rect[:,int(special_rect.shape[1]/2):])
		if left_side > 0 or right_side > 0:
			if 3*right_side > 2*left_side > right_side: # 1.5 > left_side/right_side > 0.5
				intersection = True
			elif left_side > right_side:
				left_stop = True
			else:
				right_stop = True
			

	print("-----SPECIAL DIST----- \n" ,special_distr)
	print("-----SPECIAL_DIST MID----- \n" , special_distr/2)
	print("-------SPECIAL DIST_right side------- \n", np.sum(special_rect[:,int(special_rect.shape[1]/2):]))
	print("-------SPECIAL DIST_left side------- \n", np.sum(special_rect[:,:int(special_rect.shape[1]/2)]))
	print("------------Intersection--------- \n", intersection)
	print("------------left_stop--------- \n", left_stop)
	print("------------right_stop--------- \n", right_stop)

	if debug or get_pics:
		cv2.rectangle(pre_image,(int(image.shape[1]/4),int(image.shape[0]/2), int(image.shape[1] - image.shape[1]/2), int(image.shape[0]-image.shape[0]/1.5)), (255,255,255), 2)            
                         
                            
	if debug:
		camera.preview_image_grid([[pre_image], [graph]])
    
	if not get_pics:
		graph = None
		pre_image = None

	print("finish: dl_detect_lanes")
	debug_time = Time.time() - debug_time
	print("time: ", debug_time)
    
	return lanes[0][0], lanes[1][0], graph, pre_image


def detect_lines(
	image:ImageMtx, 
	preview_steps=False, preview_result=False, get_image_data=False
) -> Tuple[float, float, ImageMtx]:
    """ A line detection function that from an inputed image detect two
    seperate lines and return them as 2nd degree polynomials.
    """
    
    # camera.preview_image(image)
    
    print("start: detect_lines")
    debug_time = Time.time()

    undistort = calibrate.get_undistort()

    fisheye_removed = undistort(image)

    warp_func, warp_back_func = get_warp_perspective_funcs(fisheye_removed, debug=False)
    warped = warp_func(fisheye_removed)
                
    # Does things to image but not warps it
    edges = dl_mark_edges(warped)

    lane_left, lane_right, graph, lanes_image = dl_detect_lanes(edges, debug=False, get_pics=True)
    
    # Calculate center offset
    camera_pos = (int(image.shape[1]/2), image.shape[0])

    # Calculate turn error
    turn_hit, turn_align, hit_point, align_vector = calc_adjust_turn(lane_left, lane_right, (camera_pos[1], camera_pos[0]))

    # _________________PREVIEW____________________

    # An image to preview result
    preview_image = undistort(image)    

    if lane_left is not None and lane_right is not None:        
        # Add colored road
        color_these_bits = fill_between_polynomials(image.shape[:2], lane_left, lane_right)
        preview_image = add_bitmap_on_image(warp_back_func(color_these_bits), preview_image, (0,255,0))

        # Draw a line inbetween lanes 
        for y in range(lanes_image.shape[1]):
            x = int((
                (lane_left[0] + lane_right[0]) * y**2 + 
                (lane_left[1] + lane_right[1]) * y +
                (lane_left[2] + lane_right[2])
            ) / 2)
            cv2.circle(lanes_image, (x, y), 2, (255, 100, 100), 2)


    # Add line to mark hit vector to turn towards
    hit_point = np.flip(np.asarray(hit_point, int))
    cv2.line(lanes_image, camera_pos, hit_point, [0,255,255], 5)

    # Add line to describe dumb path
    cv2.line(lanes_image, (camera_pos[0], 0), (camera_pos[0], lanes_image.shape[0]), (100, 100, 255), 5)
    
    # Add align vector on hit_point 
    align_vector = np.asarray((align_vector[0], -align_vector[1]))
    align_vector = (50*align_vector/np.linalg.norm(align_vector)).astype(int)
    align_point = hit_point + align_vector

    cv2.line(lanes_image, hit_point, align_point, (100, 255, 100), 5)

    if preview_steps:
        calc_error(turn_hit, turn_align, debug=True)
        camera.preview_image_grid([[image, fisheye_removed, warped], [255*edges, graph, lanes_image]])
        
    if preview_result:
        camera.preview_image_grid([[image], [result]])
    # ____________________________________________

    if get_image_data:
        return_image = lanes_image
    else:
        return_image = preview_image
        
    
    print("finish: detect_lines")
    debug_time = Time.time() - debug_time
    print("time: ", debug_time)

    return turn_hit, turn_align, return_image

# ----------------------------------------------------------------------
# Testing
# ----------------------------------------------------------------------

if __name__ == "__main__":
    image = cv2.imread(TESTFILE)    

    center_offset, left_curve, right_curve, pre_image = detect_lines(image)

    # Just so that the final frame is easy to dicern
    cv2.putText(pre_image, "FINAL FRAME", (10,pre_image.shape[0]-100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.putText(pre_image, "Center offset: {:.2f}".format(center_offset), (10,pre_image.shape[0]-70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.putText(pre_image, "Left curve: {:.2f}".format(left_curve), (10,pre_image.shape[0]-40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.putText(pre_image, "Right curve: {:.2f}".format(right_curve), (10,pre_image.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
                
    camera.preview_image(pre_image, "FINAL FRAME")
    """
        
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
