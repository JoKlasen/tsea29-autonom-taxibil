
from datetime import datetime
import opencv_stream as cam
import detection
import asyncio
from websockets import connect
import time
import time as Time
import glob
import sys
import cv2
import os
from PIL import Image
import picamera
import Pathfinding
import driving_logic

from execution_timer import exec_timer

RESULTED_IMAGE_FOLDER = './Result_640x480'


async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)
        #await websocket.recv()


def main():
    #print("Step 1 Create a camera")
    #camera = cam.create_a_camera()
    #camera = picamera.PiCamera()
    #camera.resolution = (320,256)
    #time.sleep(2)

    camera = cam.init()
    
    path = RESULTED_IMAGE_FOLDER + f'/Run_{datetime.now().strftime("%y.%m.%d-%H.%M.%S") }'    
    os.makedirs(path, exist_ok=True)
    index = 0
    
    log = open(f'{path}/log.txt', 'x')

    print("Start loop")
    left = False
    right = False
    intersection = False
    lost_intersection = False
    stop = False
    node_list, direction_list = Pathfinding.main() # List of nodes and directions to drive from pathfinding
    node_list, direction_list = [str(r) for r in node_list], [str(r) for r in direction_list]
    drive_index = 0
    drive_well = driving_logic.driving_logic(node_list, direction_list) 


    while True:

        #print(f"Iteration {index} start")
        #start_time = time.time()
        
        print("=============================================")
        print("=============================================")
        print("=============================================")
        print("=============================================")

        print("start: entire main loop")
        debug_time = Time.time()

        #print("Step 2 Capture image")
        image = cam.camera_capture_image(camera)
        
        #print("Step 3 Detect_lines")
        
        #start_calc_time = time.time()
        turn_to_hit, turn_to_align, resulting_image = detection.detect_lines(image, drive_well, get_image_data=False)
        #calc_time = time.time() - start_calc_time
        
        if drive_well.stop is True:
            print("----------> stop")
        else:
            error = detection.calc_error(turn_to_hit, turn_to_align)
        
        #print("Step 4 Create an error")
        error = detection.calc_error(turn_to_hit, turn_to_align)
        
        #print("Step 5 Create a message")
        message = f"error:e={int(error*100)}:"
        
        #print("Step 6 send to server")
        asyncio.run(send(message, "ws://localhost:8765"))

        if drive_well.stop:
            message = f"es:"
        
            #print("Step 6 send to server")
            asyncio.run(send(message, "ws://localhost:8765"))

        
        #print("Step 7 done")
        
        # Store the image that was worked upon and the resulting image
        #org_img = Image.fromarray(image)
        #org_img.save("{}/RSLT_{}_From.jpg".format(path, index))
        #rslt_img = Image.fromarray(resulting_image)
        #rslt_img.save("{}/RSLT_{}_To.jpg".format(path, index))
        
        # Store data produced
        #log.write(f'\n_______{index}_________ \nLeft: {left} \nRight: {right} \nCenter: {offset} \nError: {error} \nTotalTime: {time.time() - start_time} \nCalcTime: {calc_time}')    
        
        index += 1      

        print("finish: entire main loop")
        debug_time = Time.time() - debug_time
        print("time: ", debug_time)
        
    print("Done")


def test_folder():
    images = glob.glob("./Lanetest_320x256_temp" + "/*.jpg")

    if not len(images):
        print(f"No images in folder {folder}!")
        return None, None
    node_list, direction_list = Pathfinding.main()
    node_list, direction_list = [str(r) for r in node_list], [str(r) for r in direction_list]
    drive_well = driving_logic.driving_logic(node_list, direction_list) 

    for filename in images:
        image = cv2.imread(filename)

        exec_timer.start()

        turn_to_hit, turn_to_align, preview_image = detection.detect_lines(image, drive_well, preview_steps=False)
        if drive_well.stop is True:
            print("----------> stop")
        else:
            error = detection.calc_error(turn_to_hit, turn_to_align)
            # ~ print(error)
        
        exec_timer.end()
        
        #cam.preview_image(preview_image)
        
    exec_timer.print_memory()
    

def test_pathing():
    node_list, direction_list = Pathfinding.main()
    node_list, direction_list = [str(r) for r in node_list], [str(r) for r in direction_list]
    print(node_list)
    drive_well = driving_logic.driving_logic(node_list, direction_list)
    turn_to_hit, turn_to_align, resulting_image = detection.detect_lines(image, drive_well, get_image_data=False)
    if drive_well.stop is True:
        #send msg with stop speed
        pass
    else:
        #send normal msg
        pass
    

if __name__ == "__main__":
    main()
    
    #test_folder()

    #test_pathing()
