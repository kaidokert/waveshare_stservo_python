#!/usr/bin/env python

import sys
import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

sys.path.append("..")
from STservo_sdk import *  # Uses STServo SDK library
from device_config import load_device_port

# Default setting
BAUDRATE = 1000000  # STServo default baudrate : 1000000
DEVICENAME = load_device_port()  # Load port from YAML config

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = sts(portHandler)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

# Servo ID
sts_id = 1

# Function to calibrate the offset
def calibrate_offset(sts_id):
    comm_result, error = packetHandler.write1ByteTxRx(sts_id, STS_TORQUE_ENABLE, 128)   # referenced to SMS_STS::CalibrationOfs(u8 ID)
    if comm_result != COMM_SUCCESS:
        print("Failed to calibrate offset for ID %d: %s" % (sts_id, packetHandler.getTxRxResult(comm_result)))
    if error != 0:
        print("Error occurred for ID %d: %s" % (sts_id, packetHandler.getRxPacketError(error)))
    else:
        print("Offset calibrated for servo ID %d" % sts_id)

# Main loop to calibrate the middle position
while True:
    print("Enter command (e.g., '1c' to calibrate offset for ID 1, 'q' to quit):")
    command = input().strip()
    if command.lower() == 'q':
        break
    elif command[-1].lower() == 'c':
        try:
            sts_id = int(command[:-1])
            calibrate_offset(sts_id)
        except ValueError:
            print("Invalid ID format. Please enter a valid number followed by 'c'.")
    else:
        print("Invalid command. Please enter a valid number followed by 'c'.")

# Close port
portHandler.closePort()