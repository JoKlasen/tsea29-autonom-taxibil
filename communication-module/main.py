
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
import threading
import Pathfinding
import driving_logic

from execution_timer import exec_timer

RESULTED_IMAGE_FOLDER = './Result_320x256'

# ----------------------------------------------------------------------
# Key functions
# ----------------------------------------------------------------------

async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)
        #await websocket.recv()


    
# ----------------------------------------------------------------------
# Main loop of program
# ----------------------------------------------------------------------

class CameraThread(threading.Thread):
    
    # Debug
    MEASURE_TIME = False
    PRINT_INFO = True
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False

        self.loaded_image = None
        self.wait_cond = threading.Condition()
        
    # Will halt thread to wait for image to be produced
    def wait_for_image(self):
        with self.wait_cond:
            while self.loaded_image is None and self.running:
                self.wait_cond.wait()
            image = self.loaded_image
            self.loaded_image = None
        return image
        
    # Main loop of thread
    def run(self):
        self.running = True
    
        if self.MEASURE_TIME:
            exec_timer.start(".Run")
        
        if self.PRINT_INFO:
            print("CameraThread - Start")
                
        while self.running:
            if self.MEASURE_TIME:
                exec_timer.start(".Loop")
                
            debug_time = time.time()
            
            image = cam.capture_image(camera)
            
            # Store image and notify threads who waits on it
            with self.wait_cond:
                self.loaded_image = image
                self.wait_cond.notify()        

            if self.MEASURE_TIME:
                exec_timer.end(".Loop")


        if self.MEASURE_TIME:
            exec_timer.end(".Run")

    
    def stop(self):
        if self.PRINT_INFO:
            print("CameraThread - Stop")
        self.running = False

        with self.wait_cond:
            self.wait_cond.notify_all()
    
    
class ConverterThread(threading.Thread):
    
    MEASURE_TIME = False
    PRINT_DATA = False
    
    def __init__(self, camera_thread):
        self.camera_thread = camera_thread
        self.running = False
        
        self.loaded_image = None
        self.wait_cond = threading.Condition()

    # Will halt thread to wait for image to be produced
    def wait_for_image(self):
        with self.wait_cond:
            while self.loaded_image is None and self.running:
                self.wait_cond.wait()
            image = self.loaded_image
            self.loaded_image = None
        return image
        
    def run(self):
        
        self.running = True
        
        if self.MEASURE_TIME:
            exec_timer.start(".Run")
        
        if self.PRINT_INFO:
            print("CameraThread - Start")
                        
        while self.running:
            if self.MEASURE_TIME:
                exec_timer.start(".Loop")
            
            # Get image
            image = self.camera_thread.wait_for_image()           
            
            # Converted image
            image = detection.converted_image(image)
            
            # Store image and notify threads who waits on it
            with self.wait_cond:
                self.loaded_image = image
                self.wait_cond.notify()        

            if self.MEASURE_TIME:
                exec_timer.end(".Loop")


        if self.MEASURE_TIME:
            exec_timer.end(".Run")
            
                    
    def stop(self):
        self.running = False
    
    

class CalcThread(threading.Thread):
        
    # Debug
    MEASURE_TIME = False
    PRINT_INFO = True
    
    # Logging
    LOG_IMAGES = False
    LOG_ERRORS = False
    
    # Key functions
    SEND_TO_SERVER = True
        
    def __init__(self, converter_thread):
        threading.Thread.__init__(self)
        self.running = True
                
        self.log = None
        self.path = None
        
        self.drive_well = None
        
        self.image_producer = converter_thread


    def send_data(self, error):
        message = f"er:st={int(error*100)}:sp=2:"
        asyncio.run(send(message, "ws://localhost:8765"))

        if self.drive_well.stop:
            message = f"es:"
            asyncio.run(send(message, "ws://localhost:8765"))                


    def load_log_resources(self): 
        self.path = RESULTED_IMAGE_FOLDER + f'/Run_{datetime.now().strftime("%y.%m.%d-%H.%M.%S") }'

        if self.LOG_IMAGES or self.LOG_ERRORS:
            # Create directory to store images in
            os.makedirs(self.path, exist_ok=True)

        if self.LOG_ERRORS:
            # Open log file to write to
            log = open(f'{self.path}/log.txt', 'a')
            log.write("And then tests saved the day!\n\n\n")
            log.close()
            
    def log_images(self, index, from_image, to_image):
        # Store images
        org_img = Image.fromarray(from_image)
        org_img.save(f"{self.path}/RSLT_{index}_From.jpg")
        rslt_img = Image.fromarray(to_image)
        rslt_img.save(f"{self.path}/RSLT_{index}_To.jpg")
    
    
    def log_text(self, index, log_dict):
        # Store data produced
        log = open(f'{self.path}/log.txt', 'a')
        
        print("Writing")
        log.write(f'_______{index}_________')
        for log_item in log_dict.items():
            log.write(f'\n\t- {log_item[0]} : {str(log_item[1])}')
        
        log.write('\n\n')
        
        
    # The thread main process
    def run(self):        
        if self.PRINT_INFO:
            print("CalcThread - Start")

        if self.LOG_ERRORS or self.LOG_IMAGES:
            self.load_log_resources()
        
        
        if self.MEASURE_TIME:
            exec_timer.start(".Run")
        
        index = 0
        
        left = False
        right = False
        intersection = False
        lost_intersection = False
        stop = False
 
        node_list, direction_list, dropoff_list, dropoff_directions = Pathfinding.main("RA","RB","RD") # List of nodes and directions to drive from pathfinding
        node_list, direction_list, dropoff_list, dropoff_directions = [str(r) for r in node_list], [str(r) for r in direction_list], [str(r) for r in dropoff_list], [str(r) for r in dropoff_directions]
 
        drive_index = 0
        self.drive_well = driving_logic.driving_logic(node_list, direction_list) 
        
        while self.running:
            if self.MEASURE_TIME:
                exec_timer.start(".Loop")
            
            # Get image or wait on it
            image = self.image_producer.wait_for_image()
            
            if image is None:
                stop()
                if self.MEASURE_TIME:
                    exec_timer.end(".Loop")
                break
            
            messege = "" 
            turn_to_hit, turn_to_align, resulting_image = detection.detect_lines(image, self.drive_well, get_image_data=self.LOG_IMAGES)        
            
            
            if self.drive_well.stop is True:
                print("----------> stop")
                self.drive_well = driving_logic.driving_logic(dropoff_list, dropoff_directions)
                message = f"er:st={0}:sp=0:"
                asyncio.run(send(message, "ws://localhost:8765"))
                time.sleep(5)
                if self.drive_well.direction_list == dropoff_list:
                    print("True end reached")
                    message = f"er:st={0}:sp=0:"
                    asyncio.run(send(message, "ws://localhost:8765"))
                    break
                else:
                    print("----------> stop")
                    self.drive_well = driving_logic.driving_logic(dropoff_list, dropoff_directions)
                    message = f"er:st={0}:sp=0:"
                    asyncio.run(send(message, "ws://localhost:8765"))
                    time.sleep(5)
            else:
                error = detection.calc_error(turn_to_hit, turn_to_align, self.drive_well)
                message = f"er:st={int(error*100)}:sp=1:"
                asyncio.run(send(message, "ws://localhost:8765"))

            # Get turn_errors from data
            
            # Get final error from turn_errors

    
            #if self.SEND_TO_SERVER:
                # Send data to server
               # self.send_data(error)
            
            if self.LOG_IMAGES:
                self.log_images(index, image, resulting_image)
                
            if self.LOG_ERRORS:
                self.log_text(index, {'error': error, 'turn_to_hit': turn_to_hit, 'turn_to_align': turn_to_align})
            
            index += 1
  
            if self.MEASURE_TIME:
                exec_timer.end(".Loop")


        if self.PRINT_INFO:
            print("CalcThread - Stop")
            
        if self.MEASURE_TIME:
            exec_timer.end(".Run")
            exec_timer.print_time(".Run")
            exec_timer.print_time(".Loop")
    
    def stop(self):
        self.running = False
        

def main():
    
    camera_thread = CameraThread()
    calc_thread = CalcThread(camera_thread)
    
    camera_thread.start()
    calc_thread.start()
    
    input("")
    
    camera_thread.stop()
    calc_thread.stop()

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


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

    converter_thread = ConverterThread()
    
    converter_thread.start()
    
    
    camera_thread.stop()
    calc_thread.stop()
    

    #main()
    
    #test_folder()

    #test_pathing()
    
    
    
