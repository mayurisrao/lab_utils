import serial
import time

# Initialize serial connection
def initialize_serial(port, baudrate):
    return serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        timeout=0  # Set to 0 to manage timeout manually
    )

# Read response with a timeout
def read_response(serial_port, timeout_period, terminator):
    start_time = time.time()
    response = ""
    
    while (time.time() - start_time) < timeout_period:
        if serial_port.in_waiting > 0:
            # Read available data
            data = serial_port.read(serial_port.in_waiting).decode()
            response += data
            
            # Check if terminator is present in the response
            if terminator in response:
                # Extract the response up to the terminator
                response = response.split(terminator, 1)[0]
                return response
    
    # If we exit the loop, no response was received within the timeout period
    return None

# Main program loop
def main():
    # Configuration
    port = "/dev/ttyUSB4"      # Replace with your serial port
    baudrate = 9600      # Baud rate
    timeout = 1         # Timeout in seconds
    terminator = '\r\n'  # Termination characters (CRLF)
    
    # Initialize the serial port
    ser = initialize_serial(port, baudrate)
    
    print("SERIAL COMMUNICATION PROGRAM")
    
    while True:
        # Get command from user
        cmd = input("ENTER COMMAND (or EXIT): ").strip().upper()
        
        if cmd == "EXIT":
            ser.close()  # Close the serial port
            print("Exiting...")
            break
        
        # Add terminator to command
        cmd += terminator
        
        # Send command to instrument
        ser.write(cmd.encode())
        
        if "?" in cmd:
            # If query, read response
            print("Waiting for response...")
            response = read_response(ser, timeout, terminator)
            
            if response:
                print("RESPONSE:", response)
            else:
                print("NO RESPONSE")

if __name__ == "__main__":
    main()
