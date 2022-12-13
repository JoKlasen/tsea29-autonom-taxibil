import cv2
import numpy as np
from PIL import Image
import opencv_stream as camera
import calibrate
import math
import driving_logic
import time as Time
import math

from execution_timer import exec_timer as timer

from numbers import Number
from typing import Tuple
from camera import ImageMtx, BitmapMtx, Pol2d, Vector2d, Color


CONFIG_FILE = './config.txt'
TESTFILE =  "Lanetest_320x256_LaneMissing/LeftMirrored.jpg"

# ----- Parameters -----
# Change as required
#DEFAULT_ROI = [(700,0),(0,1000),(2000,1000),(1600,0)] # 2000x1000
#DEFAULT_ROI = [(0,180),(0,440),(640,440),(640,180)] # 640x480 180 was 130 changed offset of above part to 0
DEFAULT_ROI = [(0, .4297), (0, 1), (1, 1), (1, .4297)] #320x256

DFLT_HIT_HEIGHT = 100

MARK_EDGES_BLUR = 7
MARK_EDGES_SOBEL = 7
MARK_EDGES_SOBEL_THRESHOLD = 30
MARK_EDGES_THRESHOLD = 60

DFLT_LANE_MARGIN = 50
DFLT_MIN_TO_RECENTER_WINDOW = 10
DFLT_NUMB_WINDOWS = 20

DFLT_TURNCONST = 1
DFLT_ALIGNCONST = 1
DFLT_IGNORE_LESS = 0.04

DFLT_MID_LINE_MIN_TO_CARE = 200
DFLT_MID_OFFSET = 40
DFLT_MID_WINDOW_HEIGHT = 100
DFLT_MID_WINDOW_WIDTH = 150


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def load_config():
    
    # Get paramters from file
    config_file = open(CONFIG_FILE, 'r')
    
    config = eval(''.join(config_file.readlines()))
    
    global DEFAULT_ROI
    DEFAULT_ROI = config['default_roi']

    global DFLT_HIT_HEIGHT
    DFLT_HIT_HEIGHT = config['hit_height']

    global MARK_EDGES_BLUR
    MARK_EDGES_BLUR = config['mark_edges_blur']
    global MARK_EDGES_SOBEL
    MARK_EDGES_SOBEL = config['mark_edges_sobel']
    global MARK_EDGES_SOBEL_THRESHOLD
    MARK_EDGES_SOBEL_THRESHOLD = config['mark_edges_sobel_threshold']
    global MARK_EDGES_THRESHOLD
    MARK_EDGES_THRESHOLD = config['mark_edges_threshold']

    global DFLT_LANE_MARGIN
    DFLT_LANE_MARGIN = config['lane_margin']
    global DFLT_MIN_TO_RECENTER_WINDOW
    DFLT_MIN_TO_RECENTER_WINDOW = config['min_to_recenter_window']
    global DFLT_NUMB_WINDOWS
    DFLT_NUMB_WINDOWS = config['numb_windows']

    global DFLT_TURNCONST
    DFLT_TURNCONST = config['turn_error_const']
    global DFLT_ALIGNCONST
    DFLT_ALIGNCONST = config['align_error_const']
    global DFLT_IGNORE_LESS
    DFLT_IGNORE_LESS = config['ignore_less']

    global DFLT_MID_LINE_MIN_TO_CARE
    DFLT_MID_LINE_MIN_TO_CARE = config['mid_line_min_to_care']
    global DFLT_MID_OFFSET
    DFLT_MID_OFFSET = config['mid_offset']
    global DFLT_MID_WINDOW_HEIGHT
    DFLT_MID_WINDOW_HEIGHT = config['mid_window_height']
    global DFLT_MID_WINDOW_WIDTH
    DFLT_MID_WINDOW_WIDTH = config['mid_window_width']

load_config()


# Nice to have to not see calculations all over the place
def pol2d_over(pol2d:Pol2d, over:Number):
    """ Calculates the value of a second degree polynomial for the
    provided value.
    """
    return pol2d[0]*over**2 + pol2d[1]*over+pol2d[2]




# ----------------------------------------------------------------------
# Display data on image
# ----------------------------------------------------------------------

def add_bitmap_on_image(
    bitmap:BitmapMtx, image:ImageMtx, 
    color:Color=(0, 255, 0), weight=0.5
) -> ImageMtx:
    """ Add a bitmap onto the provided image and return the result. """
    
    timer.start() 
    
    manipulated_image = image.copy()
    manipulated_image[bitmap == 1] = np.array(color)

    timer.end()
    
    return cv2.addWeighted(manipulated_image, weight, image, 1, 0)

def preview_bitmap_on_image(
    bitmap: BitmapMtx, image: ImageMtx, 
    color:Color=(0, 255, 0)
) -> None:
    """ Previews a bitmap overlayed on an image with the provided 
    color.
    """
    image_to_show = add_bitmap_to_image(bitmap, image, color)
    camera.preview_image(bitmap)

def draw_polynomial_on_image(
    image:ImageMtx, polynomial:Pol2d, 
    color:Color=(0,255,255)
) -> None:
    """ Draws the provided second degree polynomial on the image. Image
    will be changed, not returning anything.
    """
    timer.start() 
       
    plot_over_y = np.linspace(0, image.shape[0]-1, image.shape[0])
    resulting_x = pol2d_over(polynomial, plot_over_y)
    for i in range(len(plot_over_y)):
        cv2.circle(image, (int(resulting_x[i]), int(plot_over_y[i])), 2, color, 2)

    timer.end()
        
        
def fill_between_polynomials(
    size:Vector2d, poly1:Pol2d, poly2:Pol2d, 
    debug=False
) -> BitmapMtx:
    """ Creates a bitmap where the area inbetween the two provided 
    second degree polynomials are filled with ones.
    """
    
    timer.start()
    
    bitmap = np.empty(size)
    
    # A func that have value be inside of bitmap to avoid incorrect x
    clamp = lambda x: max(min(x, bitmap.shape[1]), 0)

    for y in range(bitmap.shape[0]):
        x1 = clamp(pol2d_over(poly1, y))
        x2 = clamp(pol2d_over(poly2, y))
        
        x1 = int(x1 + 0.5) # Rounded to closest integer
        x2 = int(x2 + 0.5) # Rounded to closest integer
    
        bitmap[y, min(x1,x2):max(x1,x2)] = 1

    if debug:
        camera.preview_image(bitmap*255)
        
        
    timer.end()

    return bitmap


# ----------------------------------------------------------------------
# Calculate errors
# ----------------------------------------------------------------------


def calc_adjust_turn(
    left_lane:Pol2d, right_lane:Pol2d, 
    camera_pos:Vector2d, drive_well:driving_logic, 
    hit_height=DFLT_HIT_HEIGHT
) -> Tuple[Number, Number, Vector2d, Vector2d]:
    """ Calculate the turn required to reach a point late on road.
     
    This point is called hit point and the turns are firstly to hit
    it and than to align to it. Note that these will not bring the car
    to the position at the angle but shows how 'far away' the car is.
     
    left_lane and right_lane is a 2nd degree polynomial. 
    camera_pos = (x,y) 
    """
    
    timer.start() 
    
    
    # ------NOTE:------
    # Flip x, y axises since they are considered over the y-axis
    # -----------------
    hit_x = camera_pos[0] - hit_height
    hit_y = 0
    
    # ~ print(f"DRIVE_WELL(left:{drive_well.drive_left}, 
    #           right:{drive_well.drive_right}, forward:{drive_well.drive_forward})")

    if left_lane is not None and right_lane is not None:
        drive_well.lanes_seen = 2
        drive_well.seeing_left_lane = True
        drive_well.seeing_right_lane = True
    elif left_lane is not None:
        drive_well.lanes_seen = 1
        drive_well.seeing_left_lane = True
        drive_well.seeing_right_lane = False
    elif right_lane is not None:
        drive_well.seeing_right_lane = True
        drive_well.seeing_left_lane = False
        drive_well.lanes_seen = 1
    else:
        drive_well.lanes_seen = 0
        drive_well.seeing_left_lane = False
        drive_well.seeing_right_lane = False
        
    # Calculate lane to follow
    use_left_lane = left_lane is not None and drive_well.look_for_left_lane()
    use_right_lane = right_lane is not None and drive_well.look_for_right_lane()

    if use_left_lane and use_right_lane:
        lane = np.asarray([(left_lane[i] + right_lane[i]) / 2 for i in range(3)])
    elif use_left_lane and not use_right_lane:
        lane = left_lane
        
        offset = int(pol2d_over(left_lane, camera_pos[0])) - camera_pos[1]
        
        lane[2] = left_lane[2] + left_lane[0]*offset*offset - left_lane[1]*offset
        lane[1] = left_lane[1] - 2 * left_lane[0] * offset
        lane[0] = left_lane[0]
        
        lane[2] -= offset
        lane = np.asarray(left_lane)
    elif not use_left_lane and use_right_lane:
        lane = right_lane
        
        offset = int(pol2d_over(right_lane, camera_pos[0])) - camera_pos[1]
        
        lane[2] = right_lane[2] + right_lane[0]*offset*offset - right_lane[1]*offset
        lane[1] = right_lane[1] - 2 * right_lane[0] * offset
        lane[0] = right_lane[0]
        
        lane[2] -= offset
        lane = np.asarray(right_lane)
    else:
        lane = np.asarray([0,0,camera_pos[1]]) # Straight line                  

    hit_y += pol2d_over(lane, hit_x)
                    
    hit_vector = (hit_x - camera_pos[0], hit_y - camera_pos[1])
    # Rotate so 0 is straight forward
    hit_vector = (hit_vector[1], -hit_vector[0])
    
    # ~ print(f"new_HIT({hit_x}, {hit_y}) CAM({camera_pos})")
    # ~ print(hit_vector, camera_pos)
    
    # Calculate angle from straight forward to turn_vector
    turn_to_hit = math.atan2(hit_vector[0], hit_vector[1])
    
    align_slope = 2*lane[0]*hit_x + lane[1]
    align_vector = (1, align_slope)
    # Rotate so 0 is straight forward
    align_vector = (-align_vector[1], align_vector[0])

    # Calculate angle from straight forward to alignment to road
    turn_to_align = math.atan2(align_vector[0], align_vector[1])
            
    # ~ print(f"ALIGN({align_vector})")
    
    
    timer.end()
    
    # ~ print("finish: calc_adjust_turn")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("-   time: ", debug_time)
    
    return turn_to_hit, turn_to_align, (hit_x, hit_y), align_vector


def calc_error(
    turn_hit:Number, turn_align:Number,drive_well, 
    turnconst=DFLT_TURNCONST, alignconst=DFLT_ALIGNCONST, 
    ignore_less=DFLT_IGNORE_LESS,
    debug=False
) -> Number:
    """ Calculate the error. Positive means turn right. """
        
    timer.start()
    


    error = turn_hit*turnconst + turn_align*alignconst 

    # Ignore small errors
    if -ignore_less < error < ignore_less:
        error = 0
    if drive_well.drive_intersection:
        if drive_well.drive_right and error < 0.05 and not drive_well.seeing_right_lane:
            error = 0.1
        elif drive_well.drive_left and -0.05 < error and not drive_well.seeing_left_lane:
            error = -0.1
        elif drive_well.drive_forward and drive_well.lanes_seen == 2:
            error = 0

    if debug:
        print(f"""
        ___________________________
        Turn to hit:  {turn_hit} (x{turnconst})
        Turn to align {turn_align} (x{alignconst})
        Error:      {error}
        """)

    timer.end()

    return error

# ----------------------------------------------------------------------
# Line detection as a whole
# ----------------------------------------------------------------------


def get_warp_perspective_funcs(
    image:ImageMtx, 
    roi=None, target_roi=None, 
    debug=False
) -> ImageMtx:
    """ generates a method to warps perspective of an image so that 
    region of interest, roi, covers the target area defined by 
    target_roi. Returns an image with same characteristics.
    """

    timer.start()


    if roi == None:
        roi = [(point[0]*image.shape[1], point[1]*image.shape[0]) for point in DEFAULT_ROI]
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
    
    warp_func = lambda img: cv2.warpPerspective(img, transform_matrix, image.shape[::-1][1:] if image.ndim > 2 else image.shape[::-1], borderValue=(255,255,255)) # [1:]) <- Needed for some types of images?!
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

    
    timer.end()
    
    return warp_func, warp_back_func


def dl_mark_edges(image:ImageMtx) -> BitmapMtx:
    """ Returns an image of the provided one where the edges are
    marked.
    """

    timer.start()
    
    
    timer.start(".convert")
    
    cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

    timer.end(".convert")
    timer.start(".thresh")

    _, threshed = cv2.threshold(cvt_image[:,:,1], MARK_EDGES_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
    
    timer.end(".thresh")
    timer.start(".blur")
    
    blur_image = cv2.GaussianBlur(threshed, (MARK_EDGES_BLUR,MARK_EDGES_BLUR), 0)

    timer.end(".blur")
    timer.start(".sobel")

    sobel_x = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 1, 0, MARK_EDGES_SOBEL))
    sobel_y = np.absolute(cv2.Sobel(blur_image, cv2.CV_64F, 0, 1, MARK_EDGES_SOBEL))
    
    sobel = np.sqrt(np.square(sobel_x ** 2) + np.square(sobel_y ** 2)) 
    #sobel = (sobel_x ** 2 + sobel_y ** 2)**(1/2)

    sobel_image = np.ones_like(sobel, dtype=image.dtype)
    sobel_image[sobel < MARK_EDGES_SOBEL_THRESHOLD] = 0
    
    
    timer.end(".sobel")
    
    # ~ _, s_binary = cv2.threshold(cvt_image[:,:,2], 70, 255, cv2.THRESH_BINARY_INV)
    # ~ _, r_thresh = cv2.threshold(image[:, :, 2], 70, 255, cv2.THRESH_BINARY_INV)
    # ~ rs_binary = cv2.bitwise_and(s_binary, r_thresh)
    # ~ rs_binary_like = np.ones_like(rs_binary, dtype=image.dtype)
    # ~ rs_binary_like[threshold(rs_binary)] = 0 

    # ~ sobel_image = cv2.bitwise_or(rs_binary_like, sobel_image.astype(np.uint8))
    
    
    timer.end()
    
    return sobel_image


def get_start_positions(
    bitmap:BitmapMtx, 
    get_pics=False
) -> Tuple[Number, Number, ImageMtx]:
    """ Returns the pixel distribution of image as an array with same
    width. 
    """
    
    timer.start()
    
    
    distrubution = np.sum(
#      bitmap[:,:],  # Check whole image
#      bitmap[:int(bitmap.shape[0]/2),:],   # Above half image
        bitmap[int(bitmap.shape[0]/2):,:],  # Below half image
        axis=0
    )

    mid = int(distrubution.shape[0]/2)
    # Have lanes start at highest peek on each side of the image
    left_lane_start = np.argmax(distrubution[:mid])
    right_lane_start = np.argmax(distrubution[mid:]) + mid

    if right_lane_start == mid:
        right_lane_start = distrubution.shape[0]-1
    
    # ----------GET_PICS-----------
    graph = None
    if get_pics:
        pre_image = cv2.cvtColor(bitmap*255, cv2.COLOR_GRAY2RGB)
        
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


    timer.end()

    return left_lane_start, right_lane_start, graph


def find_lane_with_sliding_window(
    bitmap: BitmapMtx, start: Number,
    numb_windows=DFLT_NUMB_WINDOWS, 
    lane_margin=DFLT_LANE_MARGIN, 
    min_to_recenter_window=DFLT_MIN_TO_RECENTER_WINDOW,
    debug_image: ImageMtx = None, 
    square_color: Color = (255, 255, 255),
    pol_color: Color = (0, 255, 255),
    pixels_color: Color = (255, 255, 255)
) -> Tuple[Pol2d, ImageMtx]:
    """ Finds and creats a second degree polynomial that fits to 1s in
    the provided bitmap. 
    
    Will track lane through windows that slides after the position of 
    found 1s. start is where on screen the first window will be placed.
    
    If debug_image is provided it will be drawn upon.
    """
    
    timer.start()
    
    
    window_height = math.ceil(bitmap.shape[0]/numb_windows)
    current_x = start
    
    lane_pixels = [
        np.empty(0),
        np.empty(0)
    ]
    
    for win_i in range(numb_windows):
    
        win_x = (
            max(0, current_x - lane_margin),
            min(bitmap.shape[1], current_x + lane_margin)
        )
        win_y = (
            max(bitmap.shape[0] - (win_i + 1) * window_height, 0),
            bitmap.shape[0] - win_i * window_height
        )
                    
        # Find pixels in window 
        pixels_in_window = (bitmap[win_y[0]:win_y[1], win_x[0]:win_x[1]]).nonzero()
                                    
        # Remember pixels for the lane
        lane_pixels[0] = np.append(lane_pixels[0], pixels_in_window[1] + win_x[0])
        lane_pixels[1] = np.append(lane_pixels[1], pixels_in_window[0] + win_y[0])
        
        if len(pixels_in_window[0]) > min_to_recenter_window:
            # Recenter around found pixels
            current_x = int(np.mean(pixels_in_window[1])) + win_x[0]

        if debug_image is not None:
            # Displays where the window were when finding the pixels
            cv2.rectangle(debug_image,(win_x[0], win_y[0]),(win_x[1], win_y[1]), square_color, 2)


    if len(lane_pixels[1]) > 400:
        # Calculate parameters      
        polynomial = np.polyfit(lane_pixels[1], lane_pixels[0], 2)
                
        if debug_image is not None:
            # Fill pixels used to calculate line
            debug_image[lane_pixels[1].astype(int), lane_pixels[0].astype(int)] = pixels_color

            # Draw calculated line on image
            draw_polynomial_on_image(debug_image, polynomial, pol_color)

    else:
        # Store bad value since no points found
        polynomial = None

    timer.end()

    return polynomial


def find_horizontal_lines(
    bitmap:BitmapMtx, drive_well:driving_logic, 
    debug_image=None, 
    square_color:Color = (255,255,255)
) -> None:
    """ Find horizontal lines on image """
    
    timer.start()
    
    top_x = int((bitmap.shape[1] - DFLT_MID_WINDOW_WIDTH ) / 2)
    top_y = bitmap.shape[0] - DFLT_MID_WINDOW_HEIGHT - DFLT_MID_OFFSET
    bottom_x = int((bitmap.shape[1] + DFLT_MID_WINDOW_WIDTH ) / 2)
    bottom_y = bitmap.shape[0] - DFLT_MID_OFFSET
    
#   special_rect = bitmap[int(bitmap.shape[0]/2):int(bitmap.shape[0]/2 + bitmap.shape[0]/4) ,int(bitmap.shape[1]/4):int(bitmap.shape[1] - bitmap.shape[1]/4)]

    special_rect = bitmap[top_y:bottom_y, top_x:bottom_x]

    special_distr = np.sum(special_rect)
    drive_well.intersection_found = False
    drive_well.right_stop_found = False
    drive_well.left_stop_found = False
    if special_distr > 200:
        left_side = np.sum(special_rect[:,:int(special_rect.shape[1]/2)])
        right_side =np.sum(special_rect[:,int(special_rect.shape[1]/2):])
        if left_side > 0 or right_side > 0:
            if 3*right_side > 2*left_side > right_side: # 1.5 > left_side/right_side > 0.5
                drive_well.intersection_found = True
                if drive_well.drive_intersection is False:
                    drive_well.normal_driving()
            elif left_side > right_side:
                drive_well.left_stop_found = True
            else:
                drive_well.right_stop_found = True
            

    # ~ print("-----SPECIAL DIST----- \n" ,special_distr)
    # ~ print("-----SPECIAL_DIST MID----- \n" , special_distr/2)
    # ~ print("-------SPECIAL DIST_right side------- \n", np.sum(special_rect[:,int(special_rect.shape[1]/2):]))
    # ~ print("-------SPECIAL DIST_left side------- \n", np.sum(special_rect[:,:int(special_rect.shape[1]/2)]))
    # ~ print("------------Intersection--------- \n", intersection)
    # ~ print("------------left_stop--------- \n", left_stop)
    # ~ print("------------right_stop--------- \n", right_stop)

    if debug_image is not None:
        cv2.rectangle(debug_image, (top_x, top_y), (bottom_x, bottom_y), square_color, 2)
    
    timer.end()

def dl_detect_lanes(
    bitmap:BitmapMtx,drive_well,  
    debug=False, get_pics=False
) -> Tuple[Pol2d, Pol2d, ImageMtx, ImageMtx]:
    """ Takes an bitmap and returns lanes tracked on it """
     
    timer.start()
    
    # Find where pixels are concentrated and mark them as startpositions    
    graph = None
    left_lane_start, right_lane_start, graph = get_start_positions(bitmap, get_pics=get_pics or debug)
    
    pre_image = None
    if debug or get_pics:
        pre_image = cv2.cvtColor(bitmap*255, cv2.COLOR_GRAY2RGB)


    # Use sliding window technique to track lanes
    left_lane = find_lane_with_sliding_window(bitmap, left_lane_start, debug_image=pre_image, pixels_color = (0, 255 ,0))
    right_lane = find_lane_with_sliding_window(bitmap, right_lane_start, debug_image=pre_image, pixels_color = (0, 0, 255))
    
    # ~ print(f" - [ left_lane:{left_lane}, right_lane:{right_lane} ]")
    
    # Find horizontal lines on image
    find_horizontal_lines(bitmap, drive_well, pre_image)
                    
                            
    if debug:
        camera.preview_image_grid([[pre_image], [graph]])
    
    timer.end()
    
    return left_lane, right_lane, graph, pre_image


def convert_image(image:ImageMtx) -> BitmapMtx:
    undistort = calibrate.get_undistort()
    fisheye_removed = undistort(image)

    warp_func, warp_back_func = get_warp_perspective_funcs(fisheye_removed, debug=False)
    warped = warp_func(fisheye_removed)

    # Does things to image but not warps it
    edges = dl_mark_edges(warped)
    
    return edges


def detect_lines(
        image:ImageMtx,drive_well:driving_logic, 
    preview_steps=False, preview_result=False, get_image_data=False
) -> Tuple[Number, Number, ImageMtx]:

    """ A line detection function that from an inputed image detect two
    seperate lines and return them as 2nd degree polynomials.
    """
    
    # camera.preview_image(image)
    
    timer.start()
    
    load_images = get_image_data or preview_result or preview_steps

    undistort = calibrate.get_undistort()

    fisheye_removed = undistort(image)

    warp_func, warp_back_func = get_warp_perspective_funcs(fisheye_removed, debug=False)
    warped = warp_func(fisheye_removed)

    # Does things to image but not warps it
    edges = dl_mark_edges(warped)
    

    lane_left, lane_right, graph, lanes_image = dl_detect_lanes(edges,drive_well, debug=False, get_pics=load_images)
    
    # Calculate center offset
    camera_pos = (int(image.shape[1]/2), image.shape[0])
    
    drive_well.drive()

    # Calculate turn error
    turn_hit, turn_align, hit_point, align_vector = calc_adjust_turn(lane_left, lane_right, (camera_pos[1], camera_pos[0]), drive_well)

    # _________________PREVIEW____________________
    # An image to preview result
    return_image = None
    if load_images:
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


        # Add line to describe dumb path
        cv2.line(lanes_image, (camera_pos[0], 0), (camera_pos[0], lanes_image.shape[0]), (100, 100, 255), 5)

        # Add line to mark hit vector to turn towards
        hit_point = np.flip(np.asarray(hit_point, int))
        cv2.line(lanes_image, camera_pos, hit_point, [0,255,255], 3)

        
        # Add align vector on hit_point 
        align_vector = np.asarray((align_vector[0], -align_vector[1]))
        align_vector = (50*align_vector/np.linalg.norm(align_vector)).astype(int)
        align_point = hit_point + align_vector
        cv2.line(lanes_image, hit_point, align_point, (100, 255, 100), 3)
        
        cv2.circle(lanes_image, hit_point, 0, (0, 0, 0), 3)
        

        if preview_steps:
            calc_error(turn_hit, turn_align, debug=True)
            camera.preview_image_grid([[image, fisheye_removed, warped], [255*edges, graph, lanes_image]])
            
        if preview_result:          
            camera.preview_image_grid([[image], [lanes_image]])
                        
        return_image = lanes_image
    # ____________________________________________

        
    timer.end()
    
    # ~ print("finish: detect_lines")
    # ~ debug_time = Time.time() - debug_time
    # ~ print("-   time: ", debug_time)
    # ~ pixels = np.sum(edges)
    # ~ print("-   ones: ", pixels)
    # ~ print(f"-   special: {debug_time/pixels if pixels != 0 else 'Error'}")

    return turn_hit, turn_align, return_image

# ----------------------------------------------------------------------
# Testing
# ----------------------------------------------------------------------

if __name__ == "__main__":

    image = cv2.imread(TESTFILE)    
    bitmap = dl_mark_edges(np.asarray(image))
    pre_image = cv2.cvtColor(bitmap*255, cv2.COLOR_GRAY2RGB)
    pol = find_lane_with_sliding_window(bitmap, 100)
    camera.preview_image(pre_image)


    # ~ image = cv2.imread(TESTFILE)    

    # ~ center_offset, left_curve, right_curve, pre_image = detect_lines(image)

    # ~ # Just so that the final frame is easy to dicern
    # ~ cv2.putText(pre_image, "FINAL FRAME", (10,pre_image.shape[0]-100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    # ~ cv2.putText(pre_image, "Center offset: {:.2f}".format(center_offset), (10,pre_image.shape[0]-70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    # ~ cv2.putText(pre_image, "Left curve: {:.2f}".format(left_curve), (10,pre_image.shape[0]-40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    # ~ cv2.putText(pre_image, "Right curve: {:.2f}".format(right_curve), (10,pre_image.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
                
    # ~ camera.preview_image(pre_image, "FINAL FRAME")
        
    # ~ # threshold = 50
    # ~ #h_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,0], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
    # ~ #l_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,1], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)
    # ~ #s_img = cv2.cvtColor(cv2.threshold(cvt_image[:,:,2], threshold, 255, cv2.THRESH_BINARY_INV)[1], cv2.COLOR_GRAY2RGB)

    # ~ # --- PRINT HLS images as well ---
    
    # ~ cvt_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2HLS)

    # ~ h_img = cv2.cvtColor(cvt_image[:,:,0], cv2.COLOR_GRAY2RGB)
    # ~ l_img = cv2.cvtColor(cvt_image[:,:,1], cv2.COLOR_GRAY2RGB)
    # ~ s_img = cv2.cvtColor(cvt_image[:,:,2], cv2.COLOR_GRAY2RGB)

    # ~ camera.preview_image_grid([
        # ~ [h_img, l_img],
        # ~ [s_img, pre_image]
    # ~ ])
