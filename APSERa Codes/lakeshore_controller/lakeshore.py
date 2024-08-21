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
        timeout=1  # Set to 0 to manage timeout manually
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
def setup():
    # Configuration
    port = (input('port: ').strip() or "/dev/ttyUSB4")     # serial port
    baudrate = (input('baudrate: ').strip() or "9600")       # Baud rate

    
    # Initialize the serial port
    try: 
        ser = initialize_serial(port, baudrate)
        print("SERIAL COMMUNICATION SUCCESS")
    except: 
        print("SERIAL COMMUNICATION FAILED")
        
    return ser


ser = setup()    
terminator = '\r\n'  # Termination characters (CRLF)
read_timeout = 1

while True:
    # Get command from user
    cmd = input("ENTER COMMAND (or EXIT): ").strip().upper()

    if cmd == "E":
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
        response = read_response(ser, read_timeout, terminator)

    if response:
        print("RESPONSE:", response)
    else:
        print("NO RESPONSE")
