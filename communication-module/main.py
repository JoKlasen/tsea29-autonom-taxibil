#!/usr/bin/python3

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

RESULTED_IMAGE_FOLDER = '/home/g13/git/communication-module/Result_320x256'

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
    
    ##### Debug Parameters #############
    MEASURE_TIME = True
    PRINT_INFO = True
    ####################################
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.dead = False
        
        self.name = "Camera" + self.name
        
        self.loaded_image = None
        self.wait_cond = threading.Condition()
        
        self.thread_in_queue = False
        
    # Will halt thread to wait for image to be produced
    def wait_for_image(self):
        with self.wait_cond:            
            while self.loaded_image is None and self.running:
                self.thread_in_queue = True
                self.wait_cond.wait()
            image = self.loaded_image
            self.loaded_image = None
            self.thread_in_queue = False
        return image
        
    # Main loop of thread
    def run(self):
        self.running = True
        self.alive = True
        
        if self.PRINT_INFO:
            print("CameraThread - Start")
        
        camera = cam.init()

        while self.running:
            if self.MEASURE_TIME:
                exec_timer.start(".Loop")
            
            camera.grab()
            
            # Store image and notify threads who waits on it
            with self.wait_cond:
                if self.thread_in_queue:
                    ret, image = camera.retrieve()
                    
                    if ret:
                        timestamp = time.time()
                
                        self.loaded_image = (image, timestamp)
                        self.wait_cond.notify() 

            if self.MEASURE_TIME:
                exec_timer.end(".Loop")
                

        if self.PRINT_INFO:
            print("CameraThread - Stop")
            
        self.alive = False


    
    def stop(self):
        self.running = False

        with self.wait_cond:
            self.wait_cond.notify_all()
    
    
class ConverterThread(threading.Thread):
    
    ##### Debug Parameters #############
    MEASURE_TIME = True
    PRINT_INFO = True
    ####################################
    
    
    def __init__(self, camera_thread):
        threading.Thread.__init__(self)
        self.camera_thread = camera_thread
        self.running = False
        self.alive = False
        
        self.name = "Converter" + self.name
        
        self.loaded_image = None
        self.original_image = None
        self.wait_cond = threading.Condition()

    # Will halt thread to wait for image to be produced
    def wait_for_image(self):
        with self.wait_cond:
            while self.loaded_image is None and self.running:
                self.wait_cond.wait()
            images = (self.loaded_image, self.original_image)
            self.loaded_image = None
            self.original_image = None
        return images
        
    def run(self):
        self.running = True
        self.alive = True
        
        if self.PRINT_INFO:
            print("CameraThread - Start")
                        
        while self.running:
            if self.MEASURE_TIME:
                exec_timer.start(".Loop")
                        
            # Get image
            
            result = self.camera_thread.wait_for_image()      
            
            if result is None:
                self.stop()
                if self.MEASURE_TIME:
                    exec_timer.end(".Loop")
                break
            image, timestamp = result            
            
            # Converted image
            converted_image = detection.convert_image(image, preview_steps=False)
            
            # ~ print(f"ConvertThread: {- debug_time + time.time()}")
            
            # Store image and notify threads who waits on it
            with self.wait_cond:
                self.loaded_image = (converted_image, timestamp)
                self.original_image = image
                self.wait_cond.notify()        

            if self.MEASURE_TIME:
                exec_timer.end(".Loop")

        if self.PRINT_INFO:
            print("ConversionThread - Stop")
            
        self.alive = False
                    
    def stop(self):
        self.running = False
        
        with self.wait_cond:
            self.wait_cond.notify_all()
    
    

class CalcThread(threading.Thread):
        
    ###### Debug - Control #############
    MEASURE_TIME = True
    PRINT_INFO = True
    ###### Logging - Control ###########   
    LOG_IMAGES = False
    LOG_ERRORS = True
    ###### Functionality - Control #####
    SEND_TO_SERVER = True
    ####################################
        
    def __init__(self, converter_thread, path_to_drive=[]):
        threading.Thread.__init__(self)
        self.running = False
        self.alive = False
                
        self.name = "Calc" + self.name
                
        self.log_folderpath = None
        
        self.drive_well = None
        self.image_producer = converter_thread
        
        self.path = []
        self.load_path(path_to_drive)

    # ==================================================================
    # Helpers
    # ==================================================================

    def send_data(self, turn, speed):
        message = f"er:st={int(turn)}:sp={int(speed)}:"
        asyncio.run(send(message, "ws://localhost:8765"))

            
    def load_path(self, path):
        
        error = None
        
        if type(path) is not list:
            error = "Not a list."
        elif not len(path) == 3:
            error = "Path must be 3 in length."
        else:
            self.path = path
        
        
        if self.PRINT_INFO:
            if not error:
                print(f"Loaded path: {path}")
            else:
                print(f"Couldn't load path. {error} Path: {path}")

    # ==================================================================
    # Log - Logging information
    # ==================================================================

    def load_log_resources(self): 
        self.log_folderpath = RESULTED_IMAGE_FOLDER + f'/Run_{datetime.now().strftime("%y.%m.%d-%H.%M.%S") }'

        if self.LOG_IMAGES or self.LOG_ERRORS:
            # Create directory to store images in
            os.makedirs(self.log_folderpath, exist_ok=True)

        if self.LOG_ERRORS:
            # Open log file to write to
            log = open(f'{self.log_folderpath}/log.txt', 'a')
            log.write("And then tests saved the day!\n\n\n")
            log.close()
            
    def log_images(self, index, from_image, to_image):
        # Store images
        org_img = Image.fromarray(from_image)
        org_img.save(f"{self.log_folderpath}/RSLT_{index}_From.jpg")
        rslt_img = Image.fromarray(to_image)
        rslt_img.save(f"{self.log_folderpath}/RSLT_{index}_To.jpg")
    
    
    def log_text(self, index, log_dict):
        # Store data produced
        log = open(f'{self.log_folderpath}/log.txt', 'a')
        
        print("Writing")
        log.write(f'_______{index}_________')
        for log_item in log_dict.items():
            log.write(f'\n\t- {log_item[0]} : {str(log_item[1])}')
        
        log.write('\n\n')
        
        
    # ==================================================================
    # Main - Runs when thread starts
    # ==================================================================
        
    # The thread main process
    def run(self):        
        self.alive = True
        self.running = True
        
        if self.PRINT_INFO:
            print("CalcThread - Start")

        if self.LOG_ERRORS or self.LOG_IMAGES:
            self.load_log_resources()
        
        index = 0

        if not self.path:
            print("CalcThread - End")
            self.stop()
            self.alive = False
            return 
        
        node_list, direction_list, dropoff_list, dropoff_directions = Pathfinding.main(*self.path) # List of nodes and directions to drive from pathfinding
        node_list, direction_list, dropoff_list, dropoff_directions = [str(r) for r in node_list], [str(r) for r in direction_list], [str(r) for r in dropoff_list], [str(r) for r in dropoff_directions]
 
        drive_index = 0
        self.drive_well = driving_logic.driving_logic(node_list, direction_list) 
        
        while self.running:
            if self.MEASURE_TIME:
                exec_timer.start(".Loop")
            
            # Get image or wait on it
            image, original_image = self.image_producer.wait_for_image()            
            if image is None:
                self.stop()
                if self.MEASURE_TIME:
                    exec_timer.end(".Loop")
                break
            image, timestamp = image

            turn_to_hit, turn_to_align, resulting_image = detection.detect_lines(image, self.drive_well, get_image_data=self.LOG_IMAGES)

            error = detection.calc_error(turn_to_hit, turn_to_align, self.drive_well)

            print(f"Error: {error}  Delay: {time.time() - timestamp} index :{index}")
            
            if self.SEND_TO_SERVER:
                if self.drive_well.stop is True:
                    print("----------> stop")
                    self.drive_well = driving_logic.driving_logic(dropoff_list, dropoff_directions)
                    self.send_data(turn=0, speed=0) # Send to server
                    time.sleep(1)
                    
                    if self.drive_well.direction_list == dropoff_list:
                        print("True end reached")
                        self.send_data(turn=0, speed=0) # Send to server
                        self.stop()
                        if self.MEASURE_TIME:
                            exec_timer.end(".Loop")
                        break
                        
                    else:
                        print("----------> stop")
                        self.drive_well = driving_logic.driving_logic(dropoff_list, dropoff_directions)
                        self.send_data(turn=0, speed=0) # Send to server
                        time.sleep(5)
                else:
                    self.send_data(turn=int(error*100), speed=800) # Send to server


            #if self.SEND_TO_SERVER:
                # Send data to server
               # self.send_data(error)
            
            if self.LOG_IMAGES:
                self.log_images(index, original_image, resulting_image)
                
            if self.LOG_ERRORS:
                self.log_text(index, {'error': error, 'turn_to_hit': turn_to_hit, 'turn_to_align': turn_to_align})
            
            index += 1
            
            if self.MEASURE_TIME:
                exec_timer.end(".Loop")

        if self.PRINT_INFO:
            print("CalcThread - Stop")
            
            # ~ if self.MEASURE_TIME:
                # ~ exec_timer.print_time(".Loop")
    
        self.alive = False
    
    def stop(self):
        self.running = False
        

def main():
    
    path_to_drive = sys.argv[1:]
        
    camera_thread = CameraThread()
    conversion_thread = ConverterThread(camera_thread)
    calc_thread = CalcThread(conversion_thread, path_to_drive)
    
    camera_thread.start()
    conversion_thread.start()
    calc_thread.start()
    
    input("")
    
    camera_thread.stop()
    conversion_thread.stop()
    calc_thread.stop()
    
    while camera_thread.alive and conversion_thread.alive and calc_thread.alive:
        time.sleep(.1)
    
    exec_timer.print_memory()
    

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_folder():

    images = glob.glob("./Lanetest_320x256_temp" + "/*.jpg")

    if not len(images):
        print(f"No images in folder {images}!")
        return None, None
    print(sys.argv)
    node_list, direction_list, dropoff_list, dropoff_directions = Pathfinding.main("RA","RF","RC")
    node_list, direction_list = [str(r) for r in node_list], [str(r) for r in direction_list]
    drive_well = driving_logic.driving_logic(node_list, direction_list) 

    for filename in images:
        image = cv2.imread(filename)

        print(f"<<< {filename} >>> - Start")

        exec_timer.start()

        converted_image = detection.convert_image(image, preview_steps=True)

        turn_to_hit, turn_to_align, preview_image = detection.detect_lines(converted_image, drive_well, preview_result=True)
        if drive_well.stop is True:
            print("----------> stop")
        else:
            error = detection.calc_error(turn_to_hit, turn_to_align, drive_well)
            # ~ print(error)
        
        measured_time = exec_timer.end()

        print(f"<<< {filename} >>> - End (time: {measured_time})")

        
        #cam.preview_image(preview_image)
        
    exec_timer.print_memory()
    

def test_pathing():
    node_list, direction_list, dropoff_list, dropoff_directions = Pathfinding.main("RA","RB","RD")
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
    

