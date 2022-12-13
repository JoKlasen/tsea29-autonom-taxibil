
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
#import picamera
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

    #load_config()

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
    node_list, direction_list, dropoff_list, dropoff_directions = Pathfinding.main("RA","RB","RD") # List of nodes and directions to drive from pathfinding
    node_list, direction_list = [str(r) for r in node_list], [str(r) for r in direction_list]
    drive_index = 0
    drive_well = driving_logic.driving_logic(node_list, direction_list) 


    while True:

        #print(f"Iteration {index} start")
        #start_time = time.time()
        
        #print("=============================================")
        #print("=============================================")
        #print("=============================================")
        #print("=============================================")

        print("start: entire main loop")
        debug_time = Time.time()

        #print("Step 2 Capture image")
        image = cam.capture_image(camera)
        
        #print("Step 3 Detect_lines")
        
        #start_calc_time = time.time()
        turn_to_hit, turn_to_align, resulting_image = detection.detect_lines(image, drive_well, get_image_data= True, preview_steps=False)
        #calc_time = time.time() - start_calc_time
        messege = ""
        
        if drive_well.stop is True:
            if drive_well.direction_list == dropoff_list:
                print("True end reached")
                message = f"er:st={0}:sp=0:"
                asyncio.run(send(message, "ws://localhost:8765"))
                break
            else:
                print("----------> stop")
                drive_well = driving_logic(dropoff_list, dropoff_directions)
                message = f"er:st={0}:sp=0:"
                asyncio.run(send(message, "ws://localhost:8765"))
                time.sleep(5)
        else:
            error = detection.calc_error(turn_to_hit, turn_to_align, drive_well)
            message = f"er:st={int(error*100)}:sp=1:"
            asyncio.run(send(message, "ws://localhost:8765"))
        
        #print("Step 4 Create an error")
        
        #print("Step 5 Create a message")
        
        #print("Step 6 send to server")

        
        #print("Step 7 done")
        
        # Store the image that was worked upon and the resulting image
        if True:
            org_img = Image.fromarray(image)
            org_img.save("{}/RSLT_{}_From.jpg".format(path, index))
            rslt_img = Image.fromarray(resulting_image)
            rslt_img.save("{}/RSLT_{}_To.jpg".format(path, index))
        

        print("finish: entire main loop")
        debug_time = Time.time() - debug_time
        print("time: ", debug_time)
        
        # Store data produced
        log.write(f'\n_______{index}_________ \nError: {error} \TurnToAlign: {turn_to_align} \nTurnToHit: {turn_to_hit} \nCalcTime: {debug_time}')    
        
        index += 1      
        
    print("Done")


def test_folder():

    images = glob.glob("./Lanetest_320x256_Visionen" + "/*.jpg")

    if not len(images):
        print(f"No images in folder {images}!")
        return None, None
    node_list, direction_list = Pathfinding.main()
    node_list, direction_list = [str(r) for r in node_list], [str(r) for r in direction_list]
    drive_well = driving_logic.driving_logic(node_list, direction_list) 

    for filename in images:
        image = cv2.imread(filename)

        print(f"<<< {filename} >>> - Start")

        exec_timer.start()

        turn_to_hit, turn_to_align, preview_image = detection.detect_lines(image, drive_well, preview_steps=True)
        if drive_well.stop is True:
            print("----------> stop")
        else:
            error = detection.calc_error(turn_to_hit, turn_to_align)
            # ~ print(error)
        
        measured_time = exec_timer.end()

        print(f"<<< {filename} >>> - End (time: {measured_time})")

        
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
    
    
    
