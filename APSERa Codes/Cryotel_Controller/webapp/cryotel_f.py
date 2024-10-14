from flask import Flask, render_template, jsonify, request, send_file
import serial
import plotly.graph_objs as go
import plotly
from datetime import datetime
import pytz
import os
import time
import json

app = Flask(__name__)

#===========================================================================================

# cryo control variables
ser_connection_fail = False
temperature_logs = []
logging_start_time = None  # Variable to store the start time for logging
logging_end_time = None  # Variable to store the end time for logging

#===========================================================================================
# Functions for serial connection of cryo controller
def initialize_serial_connection():
    global ser_connection_fail, ser
    port = "/dev/ttyUSB1"  # or "COM3" for Windows
    baudrate = 9600
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print('Connected')
    except Exception as e:
        print('Not Connected:', e)
        ser_connection_fail = True

def send_command(command):
    global ser_connection_fail
    if ser_connection_fail:
        return 'NA'
    else:
        ser.write(command.encode('utf-8'))

        response = ''
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line == '':
                break
            response += line + '\n'
        return str(response.split('\n')[1])

def send_command_lakeshore(command):
    global ser_connection_fail
    if ser_connection_fail:
        return 'NA'
    else:
        ser.write(command.encode('utf-8'))

        response = ''
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line == '':
                break
            response += line + '\n'
        return str(response.split('\n')[1])
    
# Function to get current temperature
def get_current_temperature():
    if not ser_connection_fail:
        command = "TC\r"
        temperature = send_command(command)
        # Log the temperature with timestamp
        timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        temperature_logs.append({'timestamp': timestamp, 'temperature': temperature})
        return temperature
    return "Error"

# Function to turn on cooler
def cooler_on_command():
    # Send "COOLER=ON" command to the controller
    command = "COOLER=ON\r"
    _ = send_command(command)

# Function to turn on cooler
def cooler_off_command():
    # Send "COOLER=ON" command to the controller
    command = "COOLER=OFF\r"
    _ = send_command(command)

# Function to turn on cooler
def get_cooler_status_command():
    # Send "COOLER" command to the controller
    command = "COOLER\r"
    response = send_command(command)
    return response

# Function to turn on cooler
def get_target_temp_command():
    # Send "COOLER" command to the controller
    command = "TTARGET\r"
    response = send_command(command)
    return response

# Function to turn on cooler
def set_target_temp_command(set_target_temp_fromuser):
    # Send "COOLER" command to the controller
    command = "TTARGET=" + str(set_target_temp_fromuser) + "\r"
    send_command(command)

def get_kp_ki_kd_command():
    command = "KP\r"
    kp = float(send_command(command))

    command = "KI\r"
    ki = float(send_command(command))

    command = "KD\r"
    kd = float(send_command(command))

    return_kpid = 'Kp:' + str("{:.2f}".format(kp)) + '\nKi:' + str("{:.2f}".format(ki)) + '\nKd:' + str("{:.2f}".format(kd))
    return return_kpid

def set_kp_ki_kd_command(kp_fromuser, ki_fromuser, kd_fromuser):
    command = "KP=" + str(kp_fromuser) + "\r"
    send_command(command)

    command = "KI=" + str(ki_fromuser) + "\r"
    send_command(command)

    command = "KD=" + str(kd_fromuser) + "\r"
    send_command(command)


# Setting up dir for logs of cryo, format: {2024-09-24} {16:20:55}, {294.16} K
LOG_DIR = 'cryorun_logs'
# Check if the directory exists
if not os.path.exists(LOG_DIR):
    # Create the directory
    os.makedirs(LOG_DIR)
    print(f"Directory '{LOG_DIR}' created.")
else:
    print(f"Directory '{LOG_DIR}' already exists.")


# Function to save logs to a file
def save_logs_to_file(log_data, filename):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # Create directory if it doesn't exist

    filepath = os.path.join(LOG_DIR, f"{filename}.txt")
    with open(filepath, 'w') as f:
        for log in log_data:
            f.write(f"{log['timestamp']}, {log['temperature']} K\n")

#=========================================================================================
# Functions merging frontend to this cryo controller flask app
@app.route('/')
def index():
    return render_template('index.html')

# Assuming other imports and Flask setup are already done
temperature_dump = []
@app.route('/get_temperature', methods=['GET'])
def get_temperature():
    current_temp = get_current_temperature()  # Function to get current temperature
    temperature_dump.append(current_temp)  # Add to temperature dump
    return jsonify({'current_temp': current_temp})

@app.route('/log_temperature', methods=['POST'])
def log_temperature():
    # Save temperature data
    data = request.get_json()
    with open('temperature_log.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerows(data['log_data'])
    return jsonify({'success': True})

@app.route('/get_target_temperature')
def get_target_temperature():
    target_temp = get_target_temp_command()
    return jsonify(target_temp=target_temp + ' K')

@app.route('/get_kp_ki_kd')
def get_kp_ki_kd():
    kpid = get_kp_ki_kd_command()
    return jsonify(kpid=kpid)

@app.route('/set_target_temp', methods=['POST'])
def set_target_temp():
    target_temp = request.json.get('target_temp')  # Use request.json instead of request.args
    if target_temp:
        set_target_temp_command(int(target_temp))  # Convert to integer if needed
        return jsonify(message='Target temperature set to ' + target_temp + ' K', success=True)
    return jsonify(message='Invalid target temperature', success=False), 400

@app.route('/set_kp_ki_kd', methods=['POST'])
def set_kp_ki_kd():
    kp = request.json.get('kp')  # Use request.json to access the data
    ki = request.json.get('ki')
    kd = request.json.get('kd')
    if kp is not None and ki is not None and kd is not None:  # Check if all values are present
        set_kp_ki_kd_command(float(kp), float(ki), float(kd))
        return jsonify(message='Kp, Ki, Kd set to ' + f'{kp}, {ki}, {kd}', success=True)
    return jsonify(message='Invalid Kp, Ki, Kd values', success=False), 400



@app.route('/cooler_on', methods=['POST'])
def cooler_on():
    cooler_on_command()
    return jsonify(message='Cooler turned ON')

@app.route('/cooler_off', methods=['POST'])
def cooler_off():
    cooler_off_command()
    return jsonify(message='Cooler turned OFF')











#===========================================================================================
# lakeshore control variables
ser_lakeshore = None # to hold the lakeshore serial connection

#===========================================================================================
# Initialize serial connection with lakeshore temp display
def initialize_serial_lakeshore(port, baudrate):
    try:
        return serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
    except Exception as e:
        print(f"Error initializing serial: {e}")
        return None


# Setup serial connection
def setup_serial_lakeshore():
    global ser_lakeshore
    port = "/dev/ttyUSB2"  # Replace this with actual port input
    baudrate = 9600  # Replace this with actual baudrate input
    ser_lakeshore = initialize_serial_lakeshore(port, baudrate)
    return ser_lakeshore


# Read response with a timeout
def read_response_lakeshore(timeout_period, terminator):
    global ser_lakeshore
    start_time = time.time()
    response = ""
    while (time.time() - start_time) < timeout_period:
        if ser_lakeshore.in_waiting > 0:
            data = ser_lakeshore.read(ser_lakeshore.in_waiting).decode()
            response += data
            if terminator in response:
                response = response.split(terminator, 1)[0]
                return response


def temp_update_lakeshore():
    global ser_lakeshore
    if ser_lakeshore is None:
        return None
    read_timeout = 1
    ser_lakeshore.write('KRDG?\r\n'.encode())
    response = read_response_lakeshore(read_timeout, '\r\n')
    try:
        temperatures = [float(val) for val in response.split(',')]
        return temperatures
    except:
        return None
    
lakeshore_temperatures = []

@app.route('/get_temperature_data_lakeshore')
def get_temperature_data_lakeshore():
    temps = temp_update_lakeshore()
    if temps is None:
        return jsonify({'status': 'error', 'message': 'Serial communication failed'}), 500
    
    global lakeshore_temperatures
    lakeshore_temperatures.append(temps)  # Store the current readings

    temp_data = {'temperatures': temps}
    return jsonify(temp_data)

@app.route('/plot_temperatures')
def plot_temperatures():
    global lakeshore_temperatures
    if not lakeshore_temperatures:
        return jsonify({'status': 'error', 'message': 'No temperature data available'}), 500

    fig = go.Figure()

    for i in range(len(lakeshore_temperatures[0])):
        fig.add_trace(go.Scatter(
            x=list(range(len(lakeshore_temperatures))),
            y=[temp[i] for temp in lakeshore_temperatures],
            mode='lines',
            name=f'Sensor {i + 1}'
        ))

    fig.update_layout(title='Lakeshore Temperature Sensors',
                      xaxis_title='Time (Sample Index)',
                      yaxis_title='Temperature (K)',
                      legend_title='Sensors')
    
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', plot_json=plot_json)


#===========================================================================================
# Power Supply Variables
global ser_power
global terminator_power
global read_timeout_power

ser_power = None
terminator_power = '\r\n'
read_timeout_power = 2

# Power Supply Functions
def initialize_serial_power():
    try:
        serial_power = serial.Serial(port='/dev/ttyUSB4', baudrate=9600, timeout=read_timeout_power)
        status = remote_on_power()
        
        return serial_power
    
    except Exception as e:
        print(f"Failed to initialize serial port: {e}")
        return None

def read_response_power(serial_port, timeout_period, terminator_power):
    start_time = time.time()
    response = ""
   
    while (time.time() - start_time) < timeout_period:
        if serial_port.in_waiting > 0:
            data = serial_port.read(serial_port.in_waiting).decode()
            
            response += data
            
            if terminator_power in response:
                response = response.split(terminator_power, 1)[0].strip()
                
                # Check for the specific response
                if response == 'CH 1 ON':
                    return '..'  # Send '..' instead of 'CH 1 ON'
                
                return response  # Return the response if it's not 'CH 1 ON'

    return None

def remote_on_power():
    cmd = 'CH 1' + terminator_power
    ser_power.write(cmd.encode())

def remote_off_power():
    cmd = 'exit' + terminator_power
    ser_power.write(cmd.encode())

def get_voltage_current_power():
    global ser_power
    if ser_power:
        cmd = 'SO:VO?' + terminator_power
        ser_power.write(cmd.encode())
        voltage = read_response_power(ser_power, read_timeout_power, terminator_power)

        cmd = 'SO:CU?' + terminator_power
        ser_power.write(cmd.encode())
        current = read_response_power(ser_power, read_timeout_power, terminator_power)

        return voltage, current
    else:
        print('ser_power serial connection is None')
        return None, None

def set_voltage_current_power(voltage, current, ser_power):
    
    if ser_power is None:
        print('ser_power serial connection is None in set_voltage_current_power()')
        return jsonify(success=False, message="Serial connection not initialized"), 500

    if voltage:
        cmd = f'SO:VO {voltage}' + terminator_power
        ser_power.write(cmd.encode())
        time.sleep(0.1)

    if current:
        cmd = f'SO:CU {current}' + terminator_power
        ser_power.write(cmd.encode())

    return jsonify(success=True, message="Values updated successfully")


def get_output_voltage_current_power():    
    cmd = 'VOLT?'
    cmd += terminator_power    
    if ser_power:
        ser_power.write(cmd.encode())
        out_voltage = read_response_power(ser_power, read_timeout_power, terminator_power)
        time.sleep(0.1)
    
        cmd = 'CURR?'
        cmd += terminator_power
        ser_power.write(cmd.encode())    
        out_current = read_response_power(ser_power, read_timeout_power, terminator_power)
        
        return out_voltage, out_current
    elif ser_power == None:
        print('ser_power serial connection is None')


@app.route('/set_power_supply', methods=['POST'])
def set_power_supply():
    global ser_power
    voltage = request.json.get('voltage')
    current = request.json.get('current')

    # Set voltage and current if they are provided
    if voltage is not None:
        set_voltage_current_power(voltage, current, ser_power)
    
    if current is not None:
        set_voltage_current_power(voltage, current, ser_power)

    return jsonify(success=True, message='Voltage and/or current set'), 200



@app.route('/get_outvoltagecurrent', methods=['GET'])
def get_outvoltagecurrent():
    global ser_power
    outvoltage, outcurrent = get_output_voltage_current_power()
    
    voltage, current = get_voltage_current_power()
    
    return jsonify(voltage=voltage, current=current, outvoltage=outvoltage, outcurrent=outcurrent)



#===========================================================================================
# IIA logger Variables
# Global Variables
datalog_iia = {'time': [], 'accx': [], 'accy': [], 'accz': [], 'temperature': [], 'humidity': []}

# Function to read sensor data
# Function to read sensor data
def read_sensor_data_iia():
    while True:
        line = ser_iia.readline().decode('utf-8').rstrip()
        try:
            line = line.split(' ')
            
            # Append data to the datalog
            datalog_iia['time'].append(datetime.now())
            datalog_iia['accx'].append(float(line[13]))
            datalog_iia['accy'].append(float(line[15]))
            datalog_iia['accz'].append(float(line[17]))
            datalog_iia['temperature'].append(float(line[7]))  # Ensure this is float
            datalog_iia['humidity'].append(float(line[4]))     # Ensure this is float

            # Create a structured JSON object to return
            return {
                'time': datetime.now().isoformat(),
                'temperature': datalog_iia['temperature'],
                'humidity': datalog_iia['humidity'],
                'accx': datalog_iia['accx'],
                'accy': datalog_iia['accy'],
                'accz': datalog_iia['accz']
            }
        except Exception as e:
            print(f"Error reading sensor data: {e}")

# Flask route to get sensor data
@app.route('/get_data_iia', methods=['GET'])
def get_data_iia():
    temp = read_sensor_data_iia()
    
    return jsonify(temp)



# Initialize the serial connection
try:
    ser_iia = serial.Serial('/dev/ttyUSB3', 9600, timeout=1)
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

# Initialize the serial connection when the app starts
ser_lakeshore = setup_serial_lakeshore()


try:
    ser_power = serial.Serial(port='/dev/ttyUSB4', baudrate=9600, timeout=read_timeout_power)
    remote_on_power()
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()



initialize_serial_connection()


app.run(debug=False, host='172.16.101.78', port=5000)