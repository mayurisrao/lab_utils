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
    

# Main program loop
def setup():
    # Configuration
    port = (input('port: ').strip() or "/dev/ttyUSB1")     # serial port
    baudrate = (input('baudrate: ').strip() or "9600")       # Baud rate

    
    # Initialize the serial port
    try: 
        ser = initialize_serial(port, baudrate)
        print("SERIAL COMMUNICATION SUCCESS")
        return ser
    except: 
        print("SERIAL COMMUNICATION FAILED")
        return None

def curve_delete(cmd):
    curve = int(cmd.split(' ')[-1])
    cmd = f'CRVDEL {curve}'
    try:
        ser.write((cmd + terminator).encode())
        print(f'Curve {curve} has been deleted from datalogger')
    except:
        print('Failed')

def curve_set(cmd):
    curve = input('Which curve to configure: ')
    name = input('Give curve name (max 15 char): ')
    SN = input('Give Serial number (max 10 char): ')    
    format_ = input('Curve data format? 2 = V/K, 3 = Ohm/K, 4 = log Ohm/K: ')
    limitvalue_temp = input('Curve temperature limit in Kelvin: ')
    coef = input('Curve temperature coefficient. 1 = negative, 2 = positive: ')
    
    cmd = f'CRVHDR {curve}, {name}, {SN}, {format_}, {limitvalue_temp}, {coef}'
    try:
        ser.write((cmd + terminator).encode())
        print(f'Curve Header created for Curve {curve}')
    except:
        print('Failed')

def curve_queryheader_single():
    curve = input('Which curve to query: ')    
    cmd = f'CRVHDR? {curve}'
    try:
        ser.write((cmd + terminator).encode())
        response = read_response(ser, read_timeout, terminator)
        print(response)
    except:
        print('Failed')

def curve_entire_read():
    filename = input("Save curve data as (add .txt): ")
    curve = input("Which curve data points to save: ")
    with open(filename, 'w') as file:
        i = 0
        while True:
            cmd = f'CRVPT? {curve} {i}'
            ser.write((cmd + terminator).encode())
            response = read_response(ser, read_timeout, terminator)
            if response == "+0.00000,+00.0000" and i != 0:
                break
            file.write(response + '\n')  # Write the response to the file
            i = i + 1
            time.sleep(0.1)
            
    print(f"Data has been saved to {filename}")

def curve_queryheader_all():
    curve_index_list = list(range(1,10)) + list(range(21,29))

    curve_list = ""
    for i in curve_index_list:
        cmd = f'CRVHDR? {str(i)}'
        try:
            ser.write((cmd + terminator).encode())
            response = read_response(ser, read_timeout, terminator)
            curve_list = curve_list + (str(f'Curve {i}: '+response)) + '\n'
        except:
            print('FAILED')
            break
        time.sleep(0.1)
        
    return curve_list

def curve_point_read():  
    curve = input('Which curve to read: ')
    index = input('Index: ')

    cmd = f'CRVPT? {curve}, {index}'
    try:
        ser.write((cmd + terminator).encode())
        response = read_response(ser, read_timeout, terminator)
        print(response)
    except:
        print('Failed')





def load_curve():
    filelocation = input("Choose file to load: ") or 'dt470_raw.txt'
    data = load_curvedata_fromfile(filelocation)

    curve = input('Which curve to load to: ')
    for i in range(len(data)):
        curve_point_set(str(curve), str(i), str(data[i][1]), str(data[i][0]))
        time.sleep(0.1)

    print('Curve loaded')


# +++++++++++++++++++++++++++++++++++++++++++
def curve_point_set(curve, index, units_value, temp_value):    
    cmd = f'CRVPT {curve}, {index}, {units_value}, {temp_value}'
    try:
        ser.write((cmd + terminator).encode())
    except:
        print('Failed, please delete current curve')
        
def load_curvedata_fromfile(file_location):    
    data_list = []    
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split()
            data_list.append([float(value) for value in values])
    return data_list[::-1]



    
ser = setup()  
  
if ser == None:
    exit()
read_timeout = 1

terminator = '\r\n'

print('Commands:\n\ndelete: a curve\nsetheader: for a curve\nqueryheader: for a single curve\nquery_headerall\nread_entire_curve: all data points\nread_curve_point: single data point\nload_curve: Load curve\n\n')

while True:
    cmd_user = input("Enter command: ")
    if 'delete' in cmd_user:
        curve_delete(cmd_user)
    
    elif 'setheader' in cmd_user:
        curve_set(cmd_user)
    
    elif 'queryheader' in cmd_user:
        curve_queryheader_single()
    
    elif 'query_headerall' in cmd_user:
        print(curve_queryheader_all())

    elif 'read_entire_curve' in cmd_user:
        print(curve_entire_read())
        
    elif 'read_curve_point' in cmd_user:
        print(curve_point_read())

    elif 'load_curve' in cmd_user:
        print(load_curve())

    elif cmd_user == 'e':
        break

