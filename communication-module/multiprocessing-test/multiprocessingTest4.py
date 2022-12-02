from multiprocessing import Process, Lock, Value
from multiprocessing.shared_memory import SharedMemory
import time, array

def cam1_process(buffer1:SharedMemory, l_in:Lock, lock1:Lock, usingBuffer1:bool):
    while(True):
        if (not usingBuffer1 and lock1.acquire() and l_in.acquire()):
            time.sleep(0.5)
            print("set 1")
            buffer1.buf[:2] = bytearray([1, 2])
            lock1.release()
            l_in.release()
        #print("1, failed")

def cam2_process(buffer2:SharedMemory, l_in:Lock, lock2:Lock, usingBuffer1:bool):
    while(True):
        if (usingBuffer1 and lock2.acquire() and l_in.acquire()):
            time.sleep(0.5)
            print("set 2")
            buffer2.buf[:2] = bytearray([2, 3])
            lock2.release()
            l_in.release()
        #else:
            #print("2, failed, ", usingBuffer1)

def calc_process(output:SharedMemory, l_out:Lock):
    while True:
        if (l_out.acquire()):
            print("output")
            print(output.buf)
            l_out.release()
            time.sleep(0.3)

if __name__ == "__main__":
    debug = True
    usingBuffer1 = False

    output = SharedMemory(create=True, size=2)
    buffer1 = SharedMemory(create=True, size=2)
    buffer2 = SharedMemory(create=True, size=2)

    l_in = Lock()
    lock1 = Lock()
    lock2 = Lock()
    l_out = Lock()

    cam1 = Process(target=cam1_process, args=(buffer1, l_in, lock1, usingBuffer1))
    cam2 = Process(target=cam2_process, args=(buffer2, l_in, lock2, usingBuffer1))
    calc = Process(target=calc_process, args=(output, l_out))

    cam1.start()
    cam2.start()
    calc.start()

    while (True):
        if debug:            
            buf = array.array('b', output.buf[:])
            cambuf1 = array.array('b', buffer1.buf[:])
            cambuf2 = array.array('b', buffer2.buf[:])
            print(buf, cambuf1, cambuf2)
        if (not usingBuffer1 and lock1.acquire() and l_out.acquire()):
            print("switching to 1")
            output.buf[:] = buffer1.buf[:]
            usingBuffer1 = True
            time.sleep(0.3)
            lock1.release()
            l_out.release()
        elif (usingBuffer1 and lock2.acquire() and l_out.acquire()):
            print("switching to 2")
            output.buf[:] = buffer2.buf[:]
            usingBuffer1 = False
            time.sleep(0.3)
            lock2.release()
            l_out.release()
        else:
            print("tries")