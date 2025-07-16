from flask import Flask, render_template, jsonify, request, send_file
import serial
import plotly.graph_objs as go
import plotly
from datetime import datetime
import pytz
import os
import time
import json
import csv
import threading
from threading import Lock
import tkinter as tk
from tkinter import simpledialog
import logging
import subprocess
import yaml




logging.basicConfig(level=logging.INFO)
connection_alerts = []
#cryo_usb, lakeshore_usb, power_usb, iia_usb = get_usb_paths()
def connect_serial_with_retry1(path, message, retry_timeout=3, baudrate=9600, bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1):
    #Attempt to connect to the serial device within the given retry timeout.
    start_time = time.time()
    while time.time() - start_time < retry_timeout:
        try:
            ser = serial.Serial(
                port=path,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout
            )
            print(f"Connected to {message}")
            connection_alerts.append({
            'type': 'connectionfound',
            'device': message,
            'timestamp': datetime.now().isoformat()
            })
            return ser
        except serial.SerialException:
            print(f"Waiting for device to reconnect at {message}...")
            connection_alerts.append({
            'type': 'connectionlost',
            'device': message,
            'timestamp': datetime.now().isoformat()
            })
            time.sleep(1)
    print(f"Retry timeout exceeded for {message}")
    return None
#Access data from config.yml file
with open("config.yml", 'r') as file:
    config = yaml.safe_load(file)

app = Flask(__name__)

@app.route('/get_config', methods=['GET'])
def get_config():
    return jsonify(config)

#USB paths
cryo_usb=config['Cryo_temp']['cryo_usbpath']
lakeshore_usb=config['lakeshore_temp']['lakeshore_usbpath']
power_usb=config['power_supply']['power_usbpath']
iia_usb=config['iia_logger']['iia_usbpath']


#app = Flask(__name__)



voltage_limit = config['Cryo_temp']['cryo_usbpath']


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
    port = cryo_usb  # or "COM3" for Windows
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
    global ser
    try:
        if not ser:
            return None

        ser.write(command.encode('utf-8'))

        response = ''
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line == '':
                break
            response += line + '\n'

        lines = response.split('\n')
        return lines[1] if len(lines) > 1 else 'NA'

    except serial.SerialException:
        print("SerialException in cryo. Reconnecting...")
        try:
            ser.close()
        except:
            pass
        ser = None
        return None
        
connect_serial_with_retry1(cryo_usb,'cryo usb')

def get_current_temperature():
    global ser
    if not ser:
        ser = connect_serial_with_retry1(cryo_usb, "Cryogenic System", retry_timeout=3)
        if not ser:
            return None

    temp = send_command("TC\r")
    timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    temperature_logs.append({'timestamp': timestamp, 'temperature': temp})
    return temp


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


LOG_DIR = 'cryorun_logs'
# Check if the directory exists
if not os.path.exists(LOG_DIR):
    # Create the directory
    os.makedirs(LOG_DIR)
    print(f"Directory '{LOG_DIR}' created.")
else:
    print(f"Directory '{LOG_DIR}' already exists.")


# Function to save logs to a file
@app.route('/save_log',methods=['POST'])
def save_log():

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # Create directory if it doesn't exist

    data=request.json
    file_name_prefix=data['filename']
    log_data_lists=data['data']

    for i in range(4):
        file_name=os.path.basename(file_name_prefix[i])
        filepath=os.path.join(LOG_DIR,file_name)

        with open(filepath,'a')as f:
            for log in log_data_lists[i]:
                f.write(f"{log[0]}, {log[1:]} \n")
        f.close()
      
    return jsonify({"message":"Data appended successfully to three files"}),200

# Start the background thread
def start_logging_in_background(interval, log_data, filename):
    logging_thread = threading.Thread(target=save_log, args=())
    logging_thread.daemon = True
    logging_thread.start()

#=========================================================================================
# Functions merging frontend to this cryo controller flask app
@app.route('/')
def index():
    return render_template('upd_index1.html')

# Assuming other imports and Flask setup are already done
temperature_dump = []
@app.route('/get_temperature', methods=['GET'])
def get_temperature():
    global ser
    if not ser:
        ser = connect_serial_with_retry1(cryo_usb, "Cryogenic System", retry_timeout=3)
        if not ser:
            return jsonify({"error": "Cryo USB not connected"}), 503

    temp = get_current_temperature()
    if temp is None:
        return jsonify({"error": "Failed to read temperature"}), 500

    temperature_dump.append(temp)
    return jsonify({'current_temp': temp})

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
    print("target temperature")
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
def connect_serial_lakeshore(path, message, retry_timeout=3, baudrate=9600,
                              bytesize=serial.SEVENBITS, parity=serial.PARITY_ODD,
                              stopbits=serial.STOPBITS_ONE, timeout=1):
    start_time = time.time()
    while time.time() - start_time < retry_timeout:
        try:
            ser = serial.Serial(
                port=path,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout
            )
            print(f"Connected to {message}")
            connection_alerts.append({
            'type': 'connectionfound',
            'device': message,
            'timestamp': datetime.now().isoformat()
            })
            return ser
        except serial.SerialException:
            print(f"Waiting to reconnect {message}...")
            connection_alerts.append({
            'type': 'connectionlost',
            'device': message,
            'timestamp': datetime.now().isoformat()
            })
            time.sleep(1)
    print(f"Retry timeout exceeded for {message}")
    return None


# Response Reader
def read_response_lakeshore(timeout_period=1, terminator='\r\n'):
    global ser_lakeshore
    start_time = time.time()
    response = ""

    while time.time() - start_time < timeout_period:
        try:
            if ser_lakeshore and ser_lakeshore.in_waiting > 0:
                data = ser_lakeshore.read(ser_lakeshore.in_waiting).decode(errors='ignore')
                response += data
                if terminator in response:
                    return response.split(terminator, 1)[0]
        except serial.SerialException as e:
            print(f"Serial error while reading: {e}")
            try:
                ser_lakeshore.close()
            except:
                pass
            ser_lakeshore = None
            return None
        except Exception as e:
            print(f"Unexpected read error: {e}")
            return None
    return None


# --- Read Temperature Data ---
def temp_update_lakeshore():
    global ser_lakeshore
    if not ser_lakeshore:
        return None

    try:
        ser_lakeshore.write('KRDG?\r\n'.encode())
        response = read_response_lakeshore()

        if response is None:
            return None

        try:
            temperatures = [float(val) for val in response.split(',')]
            return temperatures
        except Exception as e:
            print(f"Parsing error: {e} | Raw response: {response}")
            return None

    except serial.SerialException:
        print("Lost connection to Lakeshore. Marking ser_lakeshore = None")
        try:
            ser_lakeshore.close()
        except:
            pass
        ser_lakeshore = None
        return None

lakeshore_temperatures = []

# --- Flask Routes ---
@app.route('/get_temperature_data_lakeshore')
def get_temperature_data_lakeshore():
    global ser_lakeshore
    if not ser_lakeshore:
        ser_lakeshore = connect_serial_lakeshore(lakeshore_usb, "Lakeshore System", retry_timeout=3)
        if not ser_lakeshore:
            return jsonify({'status': 'error', 'message': 'Lakeshore USB not connected'}), 503

    temps = temp_update_lakeshore()
    if temps is None:
        return jsonify({'status': 'error', 'message': 'Temperature read failed'}), 500

    global lakeshore_temperatures
    lakeshore_temperatures.append(temps)

    return jsonify({'temperatures': temps})


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

    fig.update_layout(
        title='Lakeshore Temperature Sensors',
        xaxis_title='Time (Sample Index)',
        yaxis_title='Temperature (K)',
        legend_title='Sensors'
    )

    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('upd_index1.html', plot_json=plot_json)

#===========================================================================================
# Power Supply Variables
global ser_power
global terminator_power
global read_timeout_power

ser_power = None
terminator_power = '\r\n'
read_timeout_power = 2

def read_response_power(serial_port, timeout_period, terminator):
    global ser_power
    start_time = time.time()
    response = ""

    while time.time() - start_time < timeout_period:
        try:
            if serial_port.in_waiting > 0:
                data = serial_port.read(serial_port.in_waiting).decode(errors='ignore')
                response += data
                if terminator in response:
                    response = response.split(terminator, 1)[0].strip()
                    return '..' if response == 'CH 1 ON' else response
        except serial.SerialException:
            print("Serial exception in read_response_power. Marking ser_power = None")
            try:
                ser_power.close()
            except:
                pass
            ser_power = None
            return None
    return None


# --- Command Helpers ---
def remote_on_power():
    global ser_power
    if not ser_power:
        return
    try:
        cmd = 'CH 1' + terminator_power
        ser_power.write(cmd.encode())
    except serial.SerialException:
        print("Lost connection in remote_on_power. Marking ser_power = None")
        try:
            ser_power.close()
        except:
            pass
        ser_power = None


def remote_off_power():
    global ser_power
    if not ser_power:
        return
    try:
        cmd = 'exit' + terminator_power
        ser_power.write(cmd.encode())
    except serial.SerialException:
        print("Lost connection in remote_off_power. Marking ser_power = None")
        try:
            ser_power.close()
        except:
            pass
        ser_power = None


def get_voltage_current_power():
    global ser_power
    if not ser_power:
        return None, None
    try:
        ser_power.write(('SO:VO?' + terminator_power).encode())
        voltage = read_response_power(ser_power, read_timeout_power, terminator_power)

        ser_power.write(('SO:CU?' + terminator_power).encode())
        current = read_response_power(ser_power, read_timeout_power, terminator_power)

        return voltage, current
    except serial.SerialException:
        print("Lost connection in get_voltage_current_power. Marking ser_power = None")
        try:
            ser_power.close()
        except:
            pass
        ser_power = None
        return None, None


def get_output_voltage_current_power():
    global ser_power
    if not ser_power:
        return None, None
    try:
        ser_power.write(('VOLT?' + terminator_power).encode())
        out_voltage = read_response_power(ser_power, read_timeout_power, terminator_power)
        time.sleep(0.1)

        ser_power.write(('CURR?' + terminator_power).encode())
        out_current = read_response_power(ser_power, read_timeout_power, terminator_power)

        return out_voltage, out_current
    except serial.SerialException:
        print("Lost connection in get_output_voltage_current_power. Marking ser_power = None")
        try:
            ser_power.close()
        except:
            pass
        ser_power = None
        return None, None


def set_voltage_current_power(voltage, current, ser_power_local):
    global ser_power
    if ser_power_local is None:
        return jsonify(success=False, message="Serial connection not initialized"), 503

    try:
        if voltage:
            cmd = f'SO:VO {voltage}' + terminator_power
            ser_power_local.write(cmd.encode())
            time.sleep(0.1)

        if current:
            cmd = f'SO:CU {current}' + terminator_power
            ser_power_local.write(cmd.encode())
    except serial.SerialException:
        print("Lost connection in set_voltage_current_power. Marking ser_power = None")
        try:
            ser_power.close()
        except:
            pass
        ser_power = None

    return jsonify(success=True, message="Values updated successfully")


# --- Flask Routes ---
@app.route('/set_power_supply', methods=['POST'])
def set_power_supply():
    global ser_power

    if ser_power is None:
        ser_power = connect_serial_with_retry1(power_usb, "Power System", retry_timeout=3)
        if ser_power is None:
            return jsonify({"error": "Power USB not connected"}), 503

    voltage = request.json.get('voltage')
    current = request.json.get('current')

    return set_voltage_current_power(voltage, current, ser_power)


@app.route('/get_outvoltagecurrent', methods=['GET'])
def get_outvoltagecurrent():
    global ser_power

    if ser_power is None:
        ser_power = connect_serial_with_retry1(power_usb, "Power System", retry_timeout=3)
        if ser_power is None:
            return jsonify({"error": "Power USB not connected"}), 503

    out_voltage, out_current = get_output_voltage_current_power()
    voltage, current = get_voltage_current_power()

    return jsonify(
        voltage=voltage,
        current=current,
        outvoltage=out_voltage,
        outcurrent=out_current
    )



#===========================================================================================
# IIA logger Variables
# Global Variables
datalog_iia = {'time': [], 'accx': [], 'accy': [], 'accz': [], 'temperature': [], 'humidity': []}


# Function to read sensor data
def read_sensor_data_iia():
    global ser_iia

    try:
        line = ser_iia.readline().decode('utf-8').rstrip()
        line = line.split(' ')

        if len(line) < 18:
            return None  # Not enough data

        datalog_iia['time'].append(datetime.now())
        datalog_iia['accx'].append(float(line[13]))
        datalog_iia['accy'].append(float(line[15]))
        datalog_iia['accz'].append(float(line[17]))
        datalog_iia['temperature'].append(float(line[7]))
        datalog_iia['humidity'].append(float(line[4]))

        return {
            'time': datetime.now().isoformat(),
            'temperature': datalog_iia['temperature'],
            'humidity': datalog_iia['humidity'],
            'accx': datalog_iia['accx'],
            'accy': datalog_iia['accy'],
            'accz': datalog_iia['accz']
        }

    except serial.SerialException:
        print("Lost connection to IIA. Marking serial as None.")
        try:
            ser_iia.close()
        except:
            pass
        ser_iia = None
        return None
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return None


@app.route('/get_data_iia', methods=['GET'])
def get_data_iia():
    global ser_iia

    if ser_iia is None:
        ser_iia = connect_serial_with_retry1(iia_usb, "IIA System", retry_timeout=3)
        if ser_iia is None:
            return jsonify({"error": "IIA USB not connected"}), 503

    data = read_sensor_data_iia()
    if data is None:
        return jsonify({"error": "Failed to read data"}), 500

    return jsonify(data)


# Initial attempt to connect (non-blocking startup)
try:
    ser_iia = connect_serial_with_retry1(iia_usb, "IIA System", retry_timeout=3)
except Exception as e:
    print(f"Initial connection failed: {e}")
    ser_iia = None


# Initialize the serial connection when the app starts
ser_lakeshore = connect_serial_lakeshore(lakeshore_usb, "Lakeshore System", retry_timeout=3)

try:
    ser_power = serial.Serial(port=power_usb, baudrate=9600, timeout=read_timeout_power)
    remote_on_power()
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

initialize_serial_connection()

#Update the alert messages in csv file
filealert=os.path.join(LOG_DIR,f"alert_log_{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y%m%d_%H%M%S')}.csv")
FIELDNAMES = ['alert_id', 'timestamp_triggered', 'alert_message', 'timestamp_acknowledged', 'name', 'comment' ]

# Create CSV file with headers if not exists
if not os.path.exists(filealert):
    with open(filealert, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

@app.route('/logalert', methods=['POST'])
def logalert():
    data = request.get_json()
    alert_id = data.get('alert_id')

    # Case 1: New alert log (only triggered)
    if not data.get('name') and not data.get('comment'):
        with open(filealert, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow({
                'alert_id': alert_id,
                'timestamp_triggered': data['timestamp_triggered'],
                'alert_message': data['alert_message'],
                'timestamp_acknowledged': '',
                'name': '',
                'comment': ''
            })
        return jsonify({'status': 'alert_logged'}), 200

    # Case 2: Acknowledge alert
    updated = False
    rows = []
    with open(filealert, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['alert_id'] == alert_id:
                row.update({
                    'timestamp_acknowledged': data['timestamp_acknowledged'],
                    'name': data['name'],
                    'comment': data['comment']                    
                })
                updated = True
            rows.append(row)

    if updated:
        with open(filealert, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        return jsonify({'status': 'alert_acknowledged'}), 200
    else:
        return jsonify({'error': 'alert_id not found'}), 404

@app.route('/ethernet-status', methods=['GET'])
def ethernet_status():
    try:
        # Run nmcli command
        result = subprocess.run(['nmcli', 'device', 'status'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # skip header
        for line in lines:
            parts = line.split()
            if 'ethernet' in parts[1].lower():
                status = parts[2].lower()
                return jsonify({'ethernet_connected': status == 'connected'})
        return jsonify({'ethernet_connected': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_connection_alerts')
def get_connection_alerts():
    global connection_alerts
    # Send and clear the queue
    alerts_to_send = connection_alerts[:]
    connection_alerts.clear()
    return jsonify(alerts_to_send)

    
app.run(debug=False, host='172.16.101.85', port=5002)
