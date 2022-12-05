
import camera as cam
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

from multiprocessing import Process, Lock, Value
from multiprocessing.shared_memory import SharedMemory

RESULTED_IMAGE_FOLDER = './Result_640x480'


async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)
        #await websocket.recv()

def cam1_process(buffer1:SharedMemory, camera:PiCamera, l_in:Lock, lock1:Lock, usingBuffer1:Value):
    while(True):
        if (not bool(usingBuffer1.value) and lock1.acquire() and l_in.acquire()):
            buffer1.buf[:] = cam.camera_capture_image(camera)
            lock1.release()
            l_in.release()

def cam2_process(buffer2:SharedMemory, camera:PiCamera, l_in:Lock, lock2:Lock, usingBuffer1:Value):
    while(True):
        if (bool(usingBuffer1.value) and lock2.acquire() and l_in.acquire()):
            buffer2.buf[:2] = cam.camera_capture_image(camera)
            lock2.release()
            l_in.release()

def main():
    #print("Step 1 Create a camera")
    #camera = cam.create_a_camera()
    camera = picamera.PiCamera()
    camera.resolution = (320,256)

    usingBuffer1 = Value('i', 0)
    
    buffer1 = SharedMemory(create=True, size=2)
    buffer2 = SharedMemory(create=True, size=2)

    l_in = Lock()
    lock1 = Lock()
    lock2 = Lock()

    cam1 = Process(target=cam1_process, args=(buffer1, l_in, lock1, usingBuffer1))
    cam2 = Process(target=cam2_process, args=(buffer2, l_in, lock2, usingBuffer1))

    cam1.start()
    cam2.start()

    time.sleep(2)
    
    path = RESULTED_IMAGE_FOLDER + f'/Run_{cam.get_timestamp()}'    
    os.mkdir(path)
    index = 0
    
    log = open(f'{path}/log.txt', 'x')

    print("Start loop")
    left = False
    right = False
    intersection = False
    lost_intersection = False
    stop = False
    node_list, direction_list = Pathfinding.main() # List of nodes and directions to drive from pathfinding
    drive_index = 0

    while True:

        #print(f"Iteration {index} start")
        #start_time = time.time()
        
        print("=============================================")
        print("=============================================")
        print("=============================================")
        print("=============================================")

        print("start: entire main loop")
        debug_time = Time.time()

        if (not bool(usingBuffer1.value) and lock1.acquire()):
            print("switching to 1")
            image = buffer1.buf[:]
            usingBuffer1.value = 1
            lock1.release()
        elif (bool(usingBuffer1.value) and lock2.acquire()):
            print("switching to 2")
            image = buffer2.buf[:]
            usingBuffer1.value = 0
            lock2.release()

        #print("Step 2 Capture image")
        #image = cam.camera_capture_image(camera)
        
        #print("Step 3 Detect_lines")
        
        #start_calc_time = time.time()
        turn_to_hit, turn_to_align, resulting_image = detection.detect_lines(image, get_image_data=True)
        #calc_time = time.time() - start_calc_time
        
        #print("Step 4 Create an error")
        error = detection.calc_error(turn_to_hit, turn_to_align)
        
        #print("Step 5 Create a message")
        message = f"error:e={int(error*100)}:"
        
        #print("Step 6 send to server")
        #asyncio.run(send(message, "ws://localhost:8765"))
        print(message)
        
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

    for filename in images:
        image = cv2.imread(filename)

        turn_to_hit, turn_to_align, preview_image = detection.detect_lines(image, preview_steps=True)
        
        error = detection.calc_error(turn_to_hit, turn_to_align)
        
        #cam.preview_image(preview_image)

def test_pathing():
    left = False
    right = False
    intersection = False
    lost_intersection = False
    stop = False
    node_list, direction_list = ['LA', 'Kors 1', 'RE', 'LF', 'Kors 2' ,'RB'], ['FORWARD', 'RIGHT', 'FORWARD', 'FORWARD', 'RIGHT', 'STOP']
    drive_index = 0
    drive_right = False
    drive_left = False
    drive_forward = False
    intersection_driving = False
    variables = drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop

    # simulate a call to detection, finding a left stop
    variables = finding_left_stop(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_intersection(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_intersection(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_right_stop(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_left_stop(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_intersection(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_intersection(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_nothing(*variables)
    # simulate a call to detection, finding a left stop
    variables = finding_right_stop(*variables)


def finding_intersection(drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop):
    left = False
    right = False
    intersection = True

    return drive_logically(drive_index, node_list, direction_list, left, right, intersection, intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop)

def finding_right_stop(drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop):
    left = False
    right = True
    intersection = False

    return drive_logically(drive_index, node_list, direction_list, left, right, intersection, intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop)

def finding_left_stop(drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop):
    left = True
    right = False
    intersection = False

    return drive_logically(drive_index, node_list, direction_list, left, right, intersection, intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop)

def finding_nothing(drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop):
    left = False
    right = False
    intersection = False

    return drive_logically(drive_index, node_list, direction_list, left, right, intersection, intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop)

def drive_logically(drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop):
    if intersection_driving is False:
        result = driving_logic.normal_driving(drive_index, node_list, direction_list, left, right, intersection)
        if result is not None:
            drive_forward , drive_left, drive_right , drive_index, intersection_driving, stop = result
    else:
        result = driving_logic.intersection_driving(intersection, lost_intersection, drive_forward, drive_right, drive_left, direction_list, node_list, drive_index)
        if result is not None:
            intersection_driving, lost_intersection, drive_forward, drive_right, drive_left = result
    return drive_index,node_list,direction_list,left,right,intersection,intersection_driving,lost_intersection, drive_forward, drive_right, drive_left, stop

if __name__ == "__main__":
    main()
    
    #test_folder()
