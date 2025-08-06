#!/usr/bin/env python
#
# *********     Ping All IDs Example      *********
#
# This script scans all possible servo IDs (0-253) to discover
# which servos are currently connected to the system.
#
# Available STServo model on this example : All models using Protocol STS
# This example is tested with a STServo and an URT
#

import sys
import os
import time
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
from STservo_sdk import *                   # Uses STServo SDK library

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
BAUDRATE                = 1000000           # STServo default baudrate : 1000000
DEVICENAME              = load_device_port()  # Load port from YAML config

# ID range to scan (servo IDs are typically 0-253)
MIN_ID = 0
MAX_ID = 253

def scan_servos():
    """Scan all possible servo IDs and return list of connected servos"""
    
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
        return []

    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        portHandler.closePort()
        return []

    print(f"\nScanning servo IDs from {MIN_ID} to {MAX_ID}...")
    print("This may take a few minutes. Please wait...\n")
    
    connected_servos = []
    
    # Scan all possible IDs
    for servo_id in range(MIN_ID, MAX_ID + 1):
        # Show progress every 50 IDs
        if servo_id % 50 == 0:
            print(f"Scanning ID: {servo_id}...")
        
        # Try to ping the servo
        sts_model_number, sts_comm_result, sts_error = packetHandler.ping(servo_id)
        
        if sts_comm_result == COMM_SUCCESS and sts_error == 0:
            servo_info = {
                'id': servo_id,
                'model_number': sts_model_number,
                'status': 'Connected'
            }
            connected_servos.append(servo_info)
            print(f"✓ Found servo at ID: {servo_id}, Model: {sts_model_number}")
        
        # Small delay to avoid overwhelming the communication
        time.sleep(0.01)
    
    # Close port
    portHandler.closePort()
    
    return connected_servos

def print_results(servos):
    """Print the scan results in a formatted way"""
    print("\n" + "="*60)
    print("SERVO SCAN RESULTS")
    print("="*60)
    
    if not servos:
        print("No servos found!")
        print("\nPossible issues:")
        print("- Check if the device is properly connected")
        print("- Verify the correct port is specified (currently: {})".format(DEVICENAME))
        print("- Ensure the servo is powered on")
        print("- Check if the baudrate is correct (currently: {})".format(BAUDRATE))
    else:
        print(f"Found {len(servos)} servo(s):")
        print("\nID  | Model Number | Status")
        print("-" * 30)
        for servo in servos:
            print(f"{servo['id']:2d}  | {servo['model_number']:11d} | {servo['status']}")
        
        print(f"\nConnected servo IDs: {[servo['id'] for servo in servos]}")
    
    print("="*60)

def main():
    """Main function"""
    print("STServo ID Scanner")
    print("This tool will scan all possible servo IDs to find connected servos.")
    print(f"Port: {DEVICENAME}")
    print(f"Baudrate: {BAUDRATE}")
    print(f"Scanning range: ID {MIN_ID} to {MAX_ID}")
    print("\nPress any key to start scanning (or ESC to quit)...")
    
    key = getch()
    if key == chr(0x1b):  # ESC key
        print("Scan cancelled.")
        return
    
    # Start scanning
    start_time = time.time()
    connected_servos = scan_servos()
    end_time = time.time()
    
    # Print results
    print_results(connected_servos)
    print(f"\nScan completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
