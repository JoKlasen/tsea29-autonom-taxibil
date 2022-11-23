import time
import subprocess
# Start both receive scripts. 
import serial
import subprocess
import asyncio
import sys

def receiveHandshakeFromUART(port):
    with serial.Serial(port, 57600) as ser:
        line = ser.readline().decode("utf-8")[:-1]
        print("in handshake: Bad first read: ")
        print(line)
        line = ser.readline().decode("utf-8")[:-1]
        print("in handshake: Real read")
        print(line)
        return line

print("Waiting for handshake on port=USB0")
port0 = receiveHandshakeFromUART('/dev/ttyUSB0')
print("Handshake received from port=USB0: " + port0)
print("Waiting for handshake on port=USB1")
port1 = receiveHandshakeFromUART('/dev/ttyUSB1')
#port1 = "sensor_module"
print("Handshake received from port=USB1: " + port1)

control_module_port = None
if ("control_module" in port0):
    print("port0 is control module")
    control_module_port = "/dev/ttyUSB0"
elif ("c" in port1):
    print("port1 is control module")
    control_module_port = "/dev/ttyUSB1"

ser0 = serial.Serial ("/dev/ttyUSB0", 57600)
ser0.write("ACK;".encode())
ser0.close()

ser1 = serial.Serial ("/dev/ttyUSB1", 57600)
ser1.write("ACK;".encode())
ser1.close()

server_val = "/home/g13/Documents/projekt/communication-module/server"
python_path = "/usr/bin/python3 "

# Read which one is which and start server with the controller serial port.
print("Starting server with args=")
print(control_module_port)
server_command = python_path + server_val + "/server/server.py " + control_module_port;
subprocess.Popen(server_command, shell=True, close_fds=True);

#Start uart receivers.
subprocess.Popen(python_path + server_val + "/uart/receiveData.py /dev/ttyUSB0", shell=True, close_fds=True)
subprocess.Popen(python_path + server_val + "/uart/receiveData.py /dev/ttyUSB1", shell=True, close_fds=True)

# Then start camera stream.
subprocess.Popen(python_path + server_val + "/camera/webserver.py", shell=True, close_fds=True);
# Then let start script exit.

time.sleep(30)
