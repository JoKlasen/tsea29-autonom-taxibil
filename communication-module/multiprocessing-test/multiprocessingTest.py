from multiprocessing import Process, Lock
from multiprocessing.shared_memory import SharedMemory
import time
import array

def cam1_process(shm1, l):
    while(True):
        time.sleep(0.1)
        l.acquire()
        print("set 1")
        array.array('b', [2], buffer=shm1.buf)
        l.release()

def cam2_process(shm2, l):
    while(True):
        time.sleep(0.1)
        l.acquire()
        print("set 2")
        array.array('b', [2], buffer=shm2.buf)
        l.release()

def calc_process(buffer, l):
    while True:
        time.sleep(1.0)
        l.acquire()
        print("output")
        a = buffer.buf[:1]
        l.release()
        print(a)

if __name__ == "__main__":
    buffer = SharedMemory(create=True, size=2)
    shm1 = SharedMemory(create=True, size=2)
    shm2 = SharedMemory(create=True, size=2)
    l_in = Lock()
    l_out = Lock()

    cam1 = Process(target=cam1_process, args=(shm1, l_in))
    cam2 = Process(target=cam2_process, args=(shm2, l_in))
    calc = Process(target=calc_process, args=(buffer, l_out))

    cam1.start()
    cam2.start()
    calc.start()

    while (True):
        time.sleep(0.3)
        #a = Array('i')
        while(not l_in.acquire() and not l_out.acquire()):
            print("tries")
        
        if (buffer == shm1):
            print("switching to 2")
            buffer == shm2
            #a = Array('i', shm2.buf[:1])
        elif (buffer == shm2):
            print("switching to 1")
            buffer == shm1
            #a = Array('i', shm1.buf[:1])
        l_in.release()
        l_out.release()
        #buffer.buf[:1] = a