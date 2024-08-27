import tkinter as tk
from tkinter import simpledialog
import random
import datetime
from matplotlib import pyplot as plt
from tkinter import simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import serial
import time
import os

# Initialize bounds for each sensor
bounds = [{'low': 40, 'high': 300} for _ in range(8)]
logging_active = True
alarm_active = False  # Track if alarm functionality is activated
log_data = []
global ser

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

def setup():
    global ser
    # Create a root Tkinter window (it won't be shown)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask user for port and baudrate via dialog boxes
    port = simpledialog.askstring("Input", "Enter serial port (default: /dev/ttyUSB4):", initialvalue="/dev/ttyUSB1")
    baudrate = simpledialog.askstring("Input", "Enter baud rate (default: 9600):", initialvalue="9600")

    # Convert baudrate to integer
    baudrate = int(baudrate)

    try:
        ser = initialize_serial(port, baudrate)
    except Exception as e:
        # Show an error message and close the application
        messagebox.showerror("Error", f"SERIAL COMMUNICATION FAILED: {e}")
        root.destroy()  # Destroy the Tkinter window and exit
        return None  # Return None or handle this case as needed

    
    while True:
        test_ser = temp_update(True)
        if test_ser == None:
            pass
        else:
            break
            
    return ser


# Read response with a timeout
def read_response(timeout_period, terminator):
    global ser
    start_time = time.time()
    response = ""
    
    while (time.time() - start_time) < timeout_period:
        if ser.in_waiting > 0:
            # Read available data
            data = ser.read(ser.in_waiting).decode()
            response += data
            
            # Check if terminator is present in the response
            if terminator in response:
                # Extract the response up to the terminator
                response = response.split(terminator, 1)[0]
                return response


def temp_update(firsttime):
    global ser
    read_timeout = 1
    # Send command to instrument
    ser.write('KRDG?\r\n'.encode())
    response = read_response(read_timeout, '\r\n')

    if firsttime:
        try:
            temperatures = [float(val) for val in response.split(',')]
            return temperatures
        except:
            return None
    else:     
        
        temperatures = [float(val) for val in response.split(',')]
        return temperatures



def update_temperature(labels, index=0):
    global ser
    temps = temp_update(False)
    if temps is None:
        return

    # Update all labels with the new temperatures
    for i, temp_value in enumerate(temps):
        labels[i].config(text=f"{temp_value} K")

    # Update sensor data and plot it
    current_time = datetime.datetime.now()
    for i, temp_value in enumerate(temps):
        sensor_data[i].append(temp_value)
        sensor_times[i].append(current_time)

        # Shift the plot window to show only the last 60 seconds of data
        time_limit = current_time - datetime.timedelta(seconds=60)
        sensor_times[i] = [t for t in sensor_times[i] if t >= time_limit]
        sensor_data[i] = sensor_data[i][-len(sensor_times[i]):]  # Keep only the relevant data points

    # Log data if logging is active
    if logging_active:
        log_data.append([current_time.strftime("%Y-%m-%d %H:%M:%S")] + [label.cget("text") for label in labels])

    # Check alarms only if alarm is active
    if alarm_active:
        check_alarms(labels)

    # Redraw the plot
    redraw_plot()

    # Schedule the next update
    root.after(2000, update_temperature, labels)



def check_alarms(labels):
    for i, label in enumerate(labels):
        temp_value = float(label.cget("text").split()[0])
        low_bound = bounds[i]['low']
        high_bound = bounds[i]['high']

        if temp_value < low_bound:
            label.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        elif temp_value > high_bound:
            label.config(highlightbackground="green", highlightcolor="green", highlightthickness=2)
        else:
            label.config(highlightbackground="black", highlightcolor="black", highlightthickness=2)

def redraw_plot():
    ax.clear()
    for i in range(8):
        if sensor_times[i]:
            ax.plot(sensor_times[i], sensor_data[i], label=f'Sensor {i+1}')

    ax.set_title("Temperature plot")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (K)")
    ax.set_xlim([datetime.datetime.now() - datetime.timedelta(seconds=60), datetime.datetime.now()])

    date_format = DateFormatter("%d-%m %H:%M:%S")
    ax.xaxis.set_major_formatter(date_format)
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))

    ax.legend(loc="upper left", fontsize="small")
    ax.grid(True)
    fig.autofmt_xdate()
    canvas.draw()

def toggle_logging():
    global logging_active
    if logging_active:
        with open("temperature_log.txt", "w") as file:
            file.write("Timestamp\tSensor 1\tSensor 2\tSensor 3\tSensor 4\tSensor 5\tSensor 6\tSensor 7\tSensor 8\n")
            for entry in log_data:
                file.write("\t".join(entry) + "\n")
        log_button.config(text="Log On", bg="green")
        logging_active = False
    else:
        log_data.clear()
        log_button.config(text="Log Off", bg="red")
        logging_active = True

def show_alarm_window():
    global alarm_active
    alarm_active = True  # Activate alarm functionality

    def accept_changes():
        global bounds
        for i in range(8):
            low_bound = int(low_bound_entries[i].get())
            high_bound = int(high_bound_entries[i].get())
            bounds[i] = {'low': low_bound, 'high': high_bound}
        alarm_window.destroy()

    def cancel_changes():
        alarm_window.destroy()

    alarm_window = tk.Toplevel(root)
    alarm_window.title("Set Alarm")
    alarm_window.configure(bg="black")

    tk.Label(alarm_window, text="Sensor", bg="black", fg="white").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(alarm_window, text="Low Bound", bg="black", fg="white").grid(row=0, column=1, padx=5, pady=5)
    tk.Label(alarm_window, text="High Bound", bg="black", fg="white").grid(row=0, column=2, padx=5, pady=5)

    low_bound_entries = []
    high_bound_entries = []

    for i in range(8):
        tk.Label(alarm_window, text=f"Sensor {i+1}", bg="black", fg="white").grid(row=i+1, column=0, padx=5, pady=5)
        low_bound_entry = tk.Entry(alarm_window, width=10)
        low_bound_entry.insert(0, bounds[i]['low'])
        low_bound_entry.grid(row=i+1, column=1, padx=5, pady=5)
        low_bound_entries.append(low_bound_entry)

        high_bound_entry = tk.Entry(alarm_window, width=10)
        high_bound_entry.insert(0, bounds[i]['high'])
        high_bound_entry.grid(row=i+1, column=2, padx=5, pady=5)
        high_bound_entries.append(high_bound_entry)

    tk.Button(alarm_window, text="Accept", command=accept_changes, bg="lightgreen", fg="black").grid(row=9, column=1, padx=5, pady=5)
    tk.Button(alarm_window, text="Cancel", command=cancel_changes, bg="lightcoral", fg="black").grid(row=9, column=2, padx=5, pady=5)

def open_terminal():
    os.system("gnome-terminal -e 'bash -c \"python lakeshore.py; exec bash\"'")

def on_enter(e):
    e.widget.config(bg="lightgray", fg="black")

def on_leave(e):
    e.widget.config(bg="gray", fg="white")






    
root = tk.Tk()


    
root.title("APSERa Lakeshore Temperature Monitor")
root.configure(bg="black")

labels = []
for i in range(8):
    heading = tk.Label(root, text=f"Sensor {i+1}", font=("Arial", 16, "bold"), bg="black", fg="white")
    heading.grid(row=(i // 4) * 2, column=i % 4, padx=10, pady=5)

    label = tk.Label(root, text="---", font=("Arial", 25), width=10, relief="solid", padx=5, pady=5,
                     bg="white", fg="red", bd=3)
    label.grid(row=(i // 4) * 2 + 1, column=i % 4, padx=10, pady=10)
    labels.append(label)
    
ser = setup()
if ser == None:
    root.destroy()
    exit()
    
sensor_data = [[] for _ in range(8)]
sensor_times = [[] for _ in range(8)]

fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, padx=10, pady=10)

button_frame = tk.Frame(root, bg="black")
button_frame.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

log_button = tk.Button(button_frame, text="Log On", font=("Arial", 12), width=15, height=2,
                       bg="gray", fg="white", bd=2, command=toggle_logging)
log_button.grid(row=0, column=0, padx=5, pady=5)

button2 = tk.Button(button_frame, text="Alarm", font=("Arial", 12), width=15, height=2,
                    bg="gray", fg="white", bd=2, command=show_alarm_window)
button2.bind("<Enter>", on_enter)
button2.bind("<Leave>", on_leave)
button2.grid(row=0, column=1, padx=5, pady=5)

button3 = tk.Button(button_frame, text="Terminal", font=("Arial", 12), width=15, height=2,
                    bg="gray", fg="white", bd=2, command=open_terminal)
button3.bind("<Enter>", on_enter)
button3.bind("<Leave>", on_leave)
button3.grid(row=0, column=2, padx=5, pady=5)

button4 = tk.Button(button_frame, text="Button 4", font=("Arial", 12), width=15, height=2,
                    bg="gray", fg="white", bd=2)
button4.bind("<Enter>", on_enter)
button4.bind("<Leave>", on_leave)
button4.grid(row=0, column=3, padx=5, pady=5)

button5 = tk.Button(button_frame, text="Button 5", font=("Arial", 12), width=15, height=2,
                    bg="gray", fg="white", bd=2)
button5.bind("<Enter>", on_enter)
button5.bind("<Leave>", on_leave)
button5.grid(row=0, column=4, padx=5, pady=5)

# Start the update process
update_temperature(labels)


root.mainloop()
