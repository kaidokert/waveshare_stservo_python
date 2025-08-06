#!/usr/bin/env python
#
# *********     Quick Servo ID Scanner      *********
#
# This script performs a smart scan to quickly find connected servos:
# 1. First scans common ID ranges (0-20)
# 2. Then optionally scans the full range (0-253)
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

# Common ID ranges to check first
QUICK_SCAN_RANGES = [
    (0, 20),    # Most common range
    (250, 253)  # Broadcast and special IDs
]

def ping_servo(packet_handler, servo_id):
    """Ping a single servo and return result"""
    sts_model_number, sts_comm_result, sts_error = packet_handler.ping(servo_id)
    
    if sts_comm_result == COMM_SUCCESS and sts_error == 0:
        return {
            'id': servo_id,
            'model_number': sts_model_number,
            'status': 'Connected'
        }
    return None

def quick_scan(packet_handler):
    """Perform a quick scan of common ID ranges"""
    print("Performing quick scan of common ID ranges...")
    connected_servos = []
    
    for start_id, end_id in QUICK_SCAN_RANGES:
        print(f"Scanning IDs {start_id}-{end_id}...")
        for servo_id in range(start_id, end_id + 1):
            result = ping_servo(packet_handler, servo_id)
            if result:
                connected_servos.append(result)
                print(f"✓ Found servo at ID: {servo_id}, Model: {result['model_number']}")
            time.sleep(0.01)  # Small delay
    
    return connected_servos

def full_scan(packet_handler, exclude_ids=None):
    """Perform a full scan of all possible IDs"""
    if exclude_ids is None:
        exclude_ids = set()
    
    print("Performing full scan (0-253)...")
    print("This will take a few minutes...")
    
    connected_servos = []
    
    for servo_id in range(0, 254):
        if servo_id in exclude_ids:
            continue
            
        # Show progress every 50 IDs
        if servo_id % 50 == 0:
            print(f"Scanning ID: {servo_id}...")
        
        result = ping_servo(packet_handler, servo_id)
        if result:
            connected_servos.append(result)
            print(f"✓ Found servo at ID: {servo_id}, Model: {result['model_number']}")
        
        time.sleep(0.01)  # Small delay
    
    return connected_servos

def print_results(servos, scan_type=""):
    """Print the scan results in a formatted way"""
    print("\n" + "="*60)
    print(f"SERVO SCAN RESULTS ({scan_type})")
    print("="*60)
    
    if not servos:
        print("No servos found!")
        print("\nPossible issues:")
        print("- Check if the device is properly connected")
        print("- Verify the correct port is specified (currently: {})".format(DEVICENAME))
        print("- Ensure the servo is powered on")
        print("- Check if the baudrate is correct (currently: {})".format(BAUDRATE))
        print("- Try running a full scan if you only ran quick scan")
    else:
        print(f"Found {len(servos)} servo(s):")
        print("\nID  | Model Number | Status")
        print("-" * 30)
        for servo in sorted(servos, key=lambda x: x['id']):
            print(f"{servo['id']:2d}  | {servo['model_number']:11d} | {servo['status']}")
        
        print(f"\nConnected servo IDs: {sorted([servo['id'] for servo in servos])}")
    
    print("="*60)

def setup_connection():
    """Setup and return port and packet handlers"""
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
        return None, None

    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        portHandler.closePort()
        return None, None
    
    return portHandler, packetHandler

def main():
    """Main function"""
    print("STServo Quick ID Scanner")
    print("This tool will intelligently scan for connected servos.")
    print(f"Port: {DEVICENAME}")
    print(f"Baudrate: {BAUDRATE}")
    
    print("\nChoose scan type:")
    print("1. Quick scan (common IDs: 0-20, 250-253) - Recommended")
    print("2. Full scan (all IDs: 0-253) - Takes longer")
    print("3. Smart scan (quick first, then ask for full)")
    print("\nPress 1, 2, 3, or ESC to quit...")
    
    key = getch()
    if key == chr(0x1b):  # ESC key
        print("Scan cancelled.")
        return
    
    # Setup connection
    portHandler, packetHandler = setup_connection()
    if not portHandler or not packetHandler:
        return
    
    try:
        start_time = time.time()
        
        if key == '1':
            # Quick scan only
            connected_servos = quick_scan(packetHandler)
            print_results(connected_servos, "Quick Scan")
            
        elif key == '2':
            # Full scan only
            connected_servos = full_scan(packetHandler)
            print_results(connected_servos, "Full Scan")
            
        elif key == '3':
            # Smart scan - quick first, then ask
            connected_servos = quick_scan(packetHandler)
            print_results(connected_servos, "Quick Scan")
            
            if connected_servos:
                print(f"\nFound {len(connected_servos)} servo(s) in quick scan.")
                print("Do you want to perform a full scan to check for more? (y/n)")
                key2 = getch()
                if key2.lower() == 'y':
                    print("\nPerforming full scan...")
                    found_ids = {servo['id'] for servo in connected_servos}
                    additional_servos = full_scan(packetHandler, exclude_ids=found_ids)
                    if additional_servos:
                        connected_servos.extend(additional_servos)
                        print_results(connected_servos, "Complete Scan")
                    else:
                        print("No additional servos found in full scan.")
            else:
                print("\nNo servos found in quick scan.")
                print("Do you want to perform a full scan? (y/n)")
                key2 = getch()
                if key2.lower() == 'y':
                    connected_servos = full_scan(packetHandler)
                    print_results(connected_servos, "Full Scan")
        else:
            print("Invalid option. Exiting.")
            return
        
        end_time = time.time()
        print(f"\nScan completed in {end_time - start_time:.2f} seconds.")
        
    finally:
        # Close port
        portHandler.closePort()

if __name__ == "__main__":
    main()
