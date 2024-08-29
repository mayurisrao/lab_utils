import tkinter as tk
from tkinter import ttk, simpledialog
import time
import threading
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime

errorlog = []
datalist = []

def read_sensor_data():
    line = ser.readline().decode('utf-8').rstrip()
    try:
        datalist.append(line)
        line = line.split(' ')
        return {
            'humidity': line[4],
            'temperature': line[7],
            'accx': float(line[13]),
            'accy': float(line[15]),
            'accz': float(line[17])
        }
    except:
        return None

global datalog
datalog = {'time': [], 'accx': [], 'accy': [], 'accz': [], 'temperature': [], 'humidity': []}

def update_data():
    data = read_sensor_data()
    if data:
        datalog['time'].append(datetime.now())
        datalog['accx'].append(data['accx'])
        datalog['accy'].append(data['accy'])
        datalog['accz'].append(data['accz'])
        datalog['temperature'].append(data['temperature'])
        datalog['humidity'].append(data['humidity'])
        
        # Update labels with new data
        temperature_label.config(text=f"{data['temperature']} °C")
        humidity_label.config(text=f"{data['humidity']} %")
        accx_label.config(text=f"{data['accx']}")
        accy_label.config(text=f"{data['accy']}")
        accz_label.config(text=f"{data['accz']}")
        
        # Update plots
        update_plots()

    root.after(1000, update_data)  # Update every 1 second

def update_plots():
    now = datetime.now()
    one_min_ago = now - pd.Timedelta(minutes=1)
    
    mask = [t > one_min_ago for t in datalog['time']]
    times = [t for t, m in zip(datalog['time'], mask) if m]
    accx = [x for x, m in zip(datalog['accx'], mask) if m]
    accy = [y for y, m in zip(datalog['accy'], mask) if m]
    accz = [z for z, m in zip(datalog['accz'], mask) if m]
    
    ax1.clear()
    ax2.clear()
    ax3.clear()
    
    ax1.plot(times, accx, 'r-')
    ax2.plot(times, accy, 'g-')
    ax3.plot(times, accz, 'b-')

    ax1.set_title('AccX over Time')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('AccX')

    ax2.set_title('AccY over Time')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('AccY')

    ax3.set_title('AccZ over Time')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('AccZ')

    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

    fig.tight_layout()

    canvas.draw()

def save_datalog():
    if not datalog['time']:
        print("No data to save.")
        return
    
    df = pd.DataFrame({
        'Time': datalog['time'],
        'AccX': datalog['accx'],
        'AccY': datalog['accy'],
        'AccZ': datalog['accz'],
        'Temp': datalog['temperature'],
        'Humidity': datalog['humidity']
    })
    
    filename = f"iiasensordata_dump/sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def ask_user_for_serial_params():
    port = simpledialog.askstring("Serial Port", "Enter the serial port:", initialvalue="/dev/ttyUSB2")
    baudrate = simpledialog.askinteger("Baud Rate", "Enter the baud rate:", initialvalue=9600)
    return port, baudrate

# Create main window
root = tk.Tk()
root.title("Sensor Data Display")

# Prompt user for serial port and baud rate
port, baudrate = ask_user_for_serial_params()

# Initialize the serial connection
try:
    ser = serial.Serial(port, baudrate, timeout=1)
except Exception as e:
    print(f"Error opening serial port: {e}")
    root.destroy()
    exit()

# Create a frame for the sensor data boxes
data_frame = tk.Frame(root, bg='black')
data_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

# Create a frame for the plot
plot_frame = ttk.Frame(root, padding="10")
plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create a figure and axes for plotting
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 6), sharex=True)

# Create a canvas for the figure
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Headings and values for the sensor data
headings = ['Temperature', 'Humidity', 'AccX', 'AccY', 'AccZ']
labels = {}

for i, heading in enumerate(headings):
    # Create a frame for each sensor value
    frame = tk.Frame(data_frame, bg='black', padx=10, pady=5)
    frame.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
    
    # Add heading label
    heading_label = tk.Label(frame, text=heading, bg='black', fg='white', font=('Arial', 12, 'bold'))
    heading_label.pack(anchor=tk.W)
    
    # Add value label
    value_label = tk.Label(frame, text='--', bg='black', fg='white', font=('Arial', 12))
    value_label.pack(anchor=tk.W)
    
    # Store the value label in the dictionary
    labels[heading] = value_label

# Assign labels to variables
temperature_label = labels['Temperature']
humidity_label = labels['Humidity']
accx_label = labels['AccX']
accy_label = labels['AccY']
accz_label = labels['AccZ']

# Create a frame for the button
button_frame = ttk.Frame(root, padding="10")
button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Add the Save Data button
save_button = ttk.Button(button_frame, text="Save Data", command=save_datalog)
save_button.grid(row=0, column=0, padx=10, pady=10)

# Start the data update loop
update_data()

# Start the GUI event loop
root.mainloop()
