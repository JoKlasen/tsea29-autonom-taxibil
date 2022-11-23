
import camera as cam
import detection
import asyncio
from websockets import connect
import time
import glob
import sys
import cv2
import os
from PIL import Image

RESULTED_IMAGE_FOLDER = './Result_640x480'


async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)
        #await websocket.recv()


def main():
	#print("Step 1 Create a camera")
	camera = cam.create_a_camera()

	time.sleep(2)
	
	path = RESULTED_IMAGE_FOLDER + f'/Run_{cam.get_timestamp()}'	
	os.mkdir(path)
	index = 0
	
	log = open(f'{path}/log.txt', 'x')

	print("Start loop")

	while True:
		#print(f"Iteration {index} start")
		start_time = time.time()
		
		#print("Step 2 Capture image")
		image = cam.camera_capture_image(camera)
		
		#print("Step 3 Detect_lines")
		
		start_calc_time = time.time()
		offset, left, right, turn, resulting_image = detection.detect_lines(image, get_image_data=True)
		calc_time = time.time() - start_calc_time
		
		#print("Step 4 Create an error")
		error = detection.calc_error(left, right, offset, turn)
		
		#print("Step 5 Create a message")
		message = f"error:e={int(-error*100)}:"
		
		#print("Step 6 send to server")
		asyncio.run(send(message, "ws://localhost:8765"))
		
		#print("Step 7 done")
		
		
		
		# Store the image that was worked upon and the resulting image
		org_img = Image.fromarray(image)
		org_img.save("{}/RSLT_{}_From.jpg".format(path, index))
		rslt_img = Image.fromarray(resulting_image)
		rslt_img.save("{}/RSLT_{}_To.jpg".format(path, index))
		
		# Store data produced
		log.write(f'\n_______{index}_________ \nLeft: {left} \nRight: {right} \nCenter: {offset} \nError: {error} \nTotalTime: {time.time() - start_time} \nCalcTime: {calc_time}')	
		
		index += 1		
		
	print("Done")


def test_folder(folder):
	images = glob.glob(folder + "/*.png")

	if not len(images):
		print(f"No images in folder {folder}!")
		return None, None

	for filename in images:
		image = cv2.imread(filename)

		offset, left, right, turn, preview_image = detection.detect_lines(image, preview_steps=True)
		
		error = detection.calc_error(left, right, offset, turn)
		
		#cam.preview_image(preview_image)
	
	


if __name__ == "__main__":
	#main()
	
	test_folder(sys.argv[1])
