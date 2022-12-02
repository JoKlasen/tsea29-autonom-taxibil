from multiprocessing import Process, Lock
import time

def cam1_process(cam1arr, l):
    while(True):
        time.sleep(0.1)
        if (l.acquire()):
            print("set 1")
            cam1arr = [1, 2]
            l.release()

def cam2_process(cam2arr, l):
    while(True):
        time.sleep(0.1)
        if (l.acquire()):
            print("set 2")
            cam2arr = [2, 3]
            l.release()

def calc_process(buffer, l:Lock):
    while True:
        time.sleep(1.0)
        if (l.acquire()):
            print("output")
            print(buffer)
            l.release()

if __name__ == "__main__":
    cam1arr = []
    cam2arr = []
    buffer = []
    l_in1 = Lock()
    l_in2 = Lock()
    l_out = Lock()

    cam1 = Process(target=cam1_process, args=(cam1arr, l_in1))
    cam2 = Process(target=cam2_process, args=(cam2arr, l_in2))
    calc = Process(target=calc_process, args=(buffer, l_out))

    cam1.start()
    cam2.start()
    calc.start()

    while (True):
        time.sleep(0.3)
        if l_in1.acquire() and l_in2.acquire() and l_out.acquire():
            if (buffer == cam1arr):
                print("switching to 2")
                buffer == cam2arr
            elif (buffer == cam2arr):
                print("switching to 1")
                buffer == cam1arr
            l_in1.release()
            l_in2.release()
            l_out.release()
        else:
            print("tries")