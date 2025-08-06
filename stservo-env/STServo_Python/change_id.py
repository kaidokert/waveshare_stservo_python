#!/usr/bin/env python
#
# *********     Gen Write Example      *********
#
#
# Available STServo model on this example : All models using Protocol STS
# This example is tested with a STServo and an URT
#

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
from STservo_sdk import *                 # Uses STServo SDK library
from device_config import load_device_port

# Default setting
BAUDRATE                    = 1000000           # STServo default baudrate : 1000000
DEVICENAME                  = load_device_port()  # Load port from YAML config
STS_MINIMUM_POSITION_VALUE  = 0           # STServo will rotate between this value
STS_MAXIMUM_POSITION_VALUE  = 4095
STS_MOVING_SPEED            = 2400        # STServo moving speed
STS_MOVING_ACC              = 50          # STServo moving acc

index = 0
sts_goal_position = [STS_MINIMUM_POSITION_VALUE, STS_MAXIMUM_POSITION_VALUE]         # Goal position

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Get methods and members of Protocol
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

# change the ID of the servo
sts_id = 1
new_id = 0
packetHandler.unLockEprom(sts_id)
sts_comm_result, sts_error = packetHandler.write1ByteTxRx(sts_id, STS_ID, new_id)
# Verify the ID change
new_id_read, comm_result, error = packetHandler.read1ByteTxRx(new_id, STS_ID)
if comm_result != COMM_SUCCESS:
    print("Failed to read new ID: %s" % packetHandler.getTxRxResult(comm_result))
if error != 0:
    print("Error occurred: %s" % packetHandler.getRxPacketError(error))
else:
    print("Successfully changed ID to %d" % new_id_read)
packetHandler.LockEprom(sts_id)
# # try to read the ID of the servo
# sts_id = 2
# sts_id_read, sts_comm_result, sts_error = packetHandler.read1ByteTxRx(sts_id, STS_ID)

# Close port
portHandler.closePort()
