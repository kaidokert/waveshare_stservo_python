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

# Default setting
BAUDRATE = 1000000  # STServo default baudrate : 1000000
DEVICENAME = '/dev/tty.usbmodem585A0085751'  # Check which port is being used on your controller
# ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*

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

# Function to enable torque
def enable_torque(sts_id):
    comm_result, error = packetHandler.write1ByteTxRx(sts_id, STS_TORQUE_ENABLE, 1)
    if comm_result != COMM_SUCCESS:
        print("Failed to enable torque for ID %d: %s" % (sts_id, packetHandler.getTxRxResult(comm_result)))
    if error != 0:
        print("Error occurred for ID %d: %s" % (sts_id, packetHandler.getRxPacketError(error)))
    else:
        print("Torque enabled for servo ID %d" % sts_id)

# Function to disable torque
def disable_torque(sts_id):
    comm_result, error = packetHandler.write1ByteTxRx(sts_id, STS_TORQUE_ENABLE, 0)
    if comm_result != COMM_SUCCESS:
        print("Failed to disable torque for ID %d: %s" % (sts_id, packetHandler.getTxRxResult(comm_result)))
    if error != 0:
        print("Error occurred for ID %d: %s" % (sts_id, packetHandler.getRxPacketError(error)))
    else:
        print("Torque disabled for servo ID %d" % sts_id)

# Main loop to switch torque on and off
while True:
    print("Enter command (e.g., '1e' to enable torque for ID 1, '255d' to disable torque for ID 255, '1e 2e' to enable torque for IDs 1 and 2, 'q' to quit):")
    command = input().strip()
    if command.lower() == 'q':
        break
    else:
        commands = command.split()
        for cmd in commands:
            if cmd[-1].lower() == 'e':
                try:
                    sts_id = int(cmd[:-1])
                    enable_torque(sts_id)
                except ValueError:
                    print("Invalid ID format for command '%s'. Please enter a valid number followed by 'e' or 'd'." % cmd)
            elif cmd[-1].lower() == 'd':
                try:
                    sts_id = int(cmd[:-1])
                    disable_torque(sts_id)
                except ValueError:
                    print("Invalid ID format for command '%s'. Please enter a valid number followed by 'e' or 'd'." % cmd)
            else:
                print("Invalid command '%s'. Please enter a valid number followed by 'e' or 'd'." % cmd)

# Close port
portHandler.closePort()