from multiprocessing import Process, Lock
from multiprocessing.shared_memory import SharedMemory
import time, array



def cam1_process(buffer1:SharedMemory, l_in:Lock, lock1:Lock):
    while(True):
        time.sleep(0.1)
        if (lock1.acquire()):
            print("set 1")
            buffer1.buf[:2] = bytearray([1, 2])
            lock1.release()

def cam2_process(buffer2:SharedMemory, l_in:Lock, lock2:Lock):
    while(True):
        time.sleep(0.1)
        if (lock2.acquire()):
            print("set 2")
            buffer2.buf[:2] = bytearray([2, 3])
            lock2.release()

def calc_process(output:SharedMemory, l_out:Lock):
    while True:
        time.sleep(1.0)
        if (l_out.acquire()):
            print("output ", array.array('b', output.buf[:]))
            l_out.release()

if __name__ == "__main__":
    output = SharedMemory(create=True, size=2)
    buffer1 = SharedMemory(create=True, size=2)
    buffer2 = SharedMemory(create=True, size=2)

    l_in = Lock()
    lock1 = Lock()
    lock2 = Lock()
    l_out = Lock()

    cam1 = Process(target=cam1_process, args=(buffer1, l_in, lock1))
    cam2 = Process(target=cam2_process, args=(buffer2, l_in, lock2))
    calc = Process(target=calc_process, args=(output, l_out))

    cam1.start()
    cam2.start()
    calc.start()

    while (True):
        time.sleep(0.3)
        if (lock1.acquire() and lock2.acquire() and l_out.acquire()):
            buf = array.array('b', output.buf[:])
            cambuf1 = array.array('b', buffer1.buf[:])
            cambuf2 = array.array('b', buffer2.buf[:])
            print(buf, cambuf1, cambuf2)
            if (buf == cambuf1):
                print("switching to 2")
                output.buf[:] = buffer2.buf[:]
            elif (buf == cambuf2):
                print("switching to 1")
                output.buf[:] = buffer1.buf[:]
            else:
                print("starting at 1")
                output.buf[:] = buffer1.buf[:]
            lock1.release()
            lock2.release()
            l_out.release()
        else:
            print("tries")