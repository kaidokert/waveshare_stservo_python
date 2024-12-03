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

# Servo ID
sts_id = 2

while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break
    # Read Voltage
    voltage, comm_result, error = packetHandler.ReadVoltage(sts_id)
    if comm_result != COMM_SUCCESS:
        print("Failed to read voltage: %s" % packetHandler.getTxRxResult(comm_result))
    if error != 0:
        print("Error occurred: %s" % packetHandler.getRxPacketError(error))
    else:
        print("Voltage: %d" % voltage)

    # Read Current
    current, comm_result, error = packetHandler.ReadCurrent(sts_id)
    if comm_result != COMM_SUCCESS:
        print("Failed to read current: %s" % packetHandler.getTxRxResult(comm_result))
    if error != 0:
        print("Error occurred: %s" % packetHandler.getRxPacketError(error))
    else:
        print("Current: %d" % current)

    # Read Temperature
    temperature, comm_result, error = packetHandler.ReadTemperature(sts_id)
    if comm_result != COMM_SUCCESS:
        print("Failed to read temperature: %s" % packetHandler.getTxRxResult(comm_result))
    if error != 0:
        print("Error occurred: %s" % packetHandler.getRxPacketError(error))
    else:
        print("Temperature: %d" % temperature)

    # Read Load
    load, comm_result, error = packetHandler.ReadLoad(sts_id)
    if comm_result != COMM_SUCCESS:
        print("Failed to read load: %s" % packetHandler.getTxRxResult(comm_result))
    if error != 0:
        print("Error occurred: %s" % packetHandler.getRxPacketError(error))
    else:
        print("Load: %d" % load)

# Close port
portHandler.closePort()