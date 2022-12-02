#https://stackoverflow.com/questions/72469003/constant-camera-grabbing-with-opencv-python-multiprocessing

import numpy as np
import cv2
from multiprocessing import Process, Queue
from multiprocessing.shared_memory import SharedMemory

def produce_frames(q):
    #get the first frame to calculate size of buffer
    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    shm = SharedMemory(create=True, size=frame.nbytes)
    framebuffer = np.ndarray(frame.shape, frame.dtype, buffer=shm.buf) #could also maybe use array.array instead of numpy, but I'm familiar with numpy
    framebuffer[:] = frame #in case you need to send the first frame to the main process
    q.put(shm) #send the buffer back to main
    q.put(frame.shape) #send the array details
    q.put(frame.dtype)
    try:
        while True:
            cap.read(framebuffer)
    except KeyboardInterrupt:
        pass
    finally:
        shm.close() #call this in all processes where the shm exists
        shm.unlink() #call from only one process

def consume_frames(q):
    shm = q.get() #get the shared buffer
    shape = q.get()
    dtype = q.get()
    framebuffer = np.ndarray(shape, dtype, buffer=shm.buf) #reconstruct the array
    try:
        while True:
            cv2.imshow("window title", framebuffer)
            cv2.waitKey(100)
    except KeyboardInterrupt:
        pass
    finally:
        shm.close()

if __name__ == "__main__":
    q = Queue()
    producer = Process(target=produce_frames, args=(q,))
    producer.start()
    consume_frames(q)