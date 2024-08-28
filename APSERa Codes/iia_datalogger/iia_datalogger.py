import tkinter as tk
from tkinter import ttk
import time
import threading
import serial

errorlog = []
datalist= []
# Dummy function to simulate data reading
def read_sensor_data():
    
    line = ser.readline().decode('utf-8').rstrip()
    #print(line)
    if temp:
        # Append the decoded string to the list
        datalist.append(line)
        line = line.split(' ')
        
    
    # Print the last element in the list every second
    if data_list:
        trytemp = [line[4], line[7], line[13], line[15], line[17]]
        
    return {
        'humidity': line[4],
        'temperature': line[7],
        'accx': line[13],
        'accy': line[15],
        'accz': line[17]
        }
 
global datalog
datalog = []

def update_data():
    # Get sensor data
    data = read_sensor_data()
    datalog.append(data)

    try: 
        # Update labels with new data
        temperature_label.config(text=f"Temperature: {data['temperature']} °C")
        humidity_label.config(text=f"Humidity: {data['humidity']} %")
        accx_label.config(text=f"AccX: {data['accx']}")
        accy_label.config(text=f"AccY: {data['accy']}")
        accz_label.config(text=f"AccZ: {data['accz']}")
    except:
        pass
    # Schedule next update
    root.after(1000, update_data)  # Update every 1 second

  

# Create main window
root = tk.Tk()
root.title("Sensor Data Display")

# Create a frame for the labels
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Labels for displaying sensor data
temperature_label = ttk.Label(frame, text="Temperature: --")
temperature_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

humidity_label = ttk.Label(frame, text="Humidity: --")
humidity_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

accx_label = ttk.Label(frame, text="AccX: --")
accx_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

accy_label = ttk.Label(frame, text="AccY: --")
accy_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

accz_label = ttk.Label(frame, text="AccZ: --")
accz_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)

ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
# Start the data update loop
update_data()

# Start the GUI event loop
root.mainloop()

