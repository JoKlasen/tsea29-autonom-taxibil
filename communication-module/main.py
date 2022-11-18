
import camera as cam
import detection
import asyncio
from websockets import connect
import time
import glob
import sys
import cv2

async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)
        #await websocket.recv()


def main():
	print("Step 1 Create a camera")
	camera = cam.create_a_camera()

	time.sleep(2)

	while True:
		print("Step 2 Capture image")
		image = cam.camera_capture_image(camera)
		
		print("Step 3 Detect_lines")
		offset, left, right, _ = detection.detect_lines(image)
		
		print("Step 4 Create an error")
		turnconst = 1.5
		offsetconst = 1.5
		error = (left+right)*turnconst + offset * offsetconst 
		
		print("Step 5 Create a message")
		message = f"ERROR:{error}:"
		
		print("Step 6 send to server")
		asyncio.run(send(message, "ws://localhost:8765"))
		
		print("Step 7 done")


def test_folder(folder):
	images = glob.glob(folder + "/*.png")

	if not len(images):
		print(f"No images in folder {folder}!")
		return None, None

	for filename in images:
		image = cv2.imread(filename)

		offset, left, right, preview_image = detection.detect_lines(image, preview_steps=True)
		
		#cam.preview_image(preview_image)
	
	


if __name__ == "__main__":
	#main()
	
	test_folder(sys.argv[1])
