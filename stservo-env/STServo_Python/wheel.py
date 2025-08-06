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
import yaml

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

def load_device_port():
    """Load device port from YAML configuration file"""
    try:
        config_file = os.path.join(os.path.dirname(__file__), '..', 'device_port.yaml')
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            return config.get('device_port', '/dev/ttyACM0')
    except FileNotFoundError:
        print("Warning: device_port.yaml not found. Using default port /dev/ttyACM0")
        print("Run check_port.py first to detect your device port.")
        return '/dev/ttyACM0'
    except Exception as e:
        print(f"Warning: Error reading device_port.yaml: {e}")
        return '/dev/ttyACM0'

# Default setting
STS_ID                      = 0                 # STServo ID : 1
BAUDRATE                    = 1000000           # STServo default baudrate : 1000000
DEVICENAME                  = load_device_port()  # Load port from YAML config
STS_MOVING_SPEED0           = 2400        # STServo moving speed
STS_MOVING_SPEED1           = -2400       # STServo moving speed
STS_MOVING_ACC              = 50          # STServo moving acc

index = 0
sts_move_speed = [STS_MOVING_SPEED0, 0, STS_MOVING_SPEED1, 0]

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

sts_comm_result, sts_error = packetHandler.WheelMode(STS_ID)
if sts_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(sts_comm_result))
elif sts_error != 0:
    print("%s" % packetHandler.getRxPacketError(sts_error))
while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    # Write STServo goal position/moving speed/moving acc
    sts_comm_result, sts_error = packetHandler.WriteSpec(STS_ID, sts_move_speed[index], STS_MOVING_ACC)
    if sts_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(sts_comm_result))
    if sts_error != 0:
        print("%s" % packetHandler.getRxPacketError(sts_error))

    # Change move speed
    index += 1
    if index == 4:
        index = 0

# Close port
portHandler.closePort()
