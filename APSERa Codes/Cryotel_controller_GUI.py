import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import serial
from datetime import datetime
import getpass
import os


port = '/dev/ttyUSB1'
ser_connection_fail = False  # Initialize ser_connection_fail outside the try block

# Initialize serial connection
try:
    ser = serial.Serial(port, baudrate=9600, timeout=1)
except:
    ser_connection_fail = True

temperature_log = []  # List to store temperature log entries

# Default query interval and unit
query_interval = 1
query_unit = "seconds"

# Function to send command and receive response
def send_command(command):
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

#AVC COMMANDS
# Function to update temperature display
def get_temperature_command():
    # Send "TC" command to the controller
    command = "TC\r"
    temperature = send_command(command)
    
    return temperature

# Function to turn on cooler
def cooler_on_command():
    # Send "COOLER=ON" command to the controller
    command = "COOLER=ON\r"
    response = send_command(command)

# Function to turn on cooler
def cooler_off_command():
    # Send "COOLER=ON" command to the controller
    command = "COOLER=OFF\r"
    response = send_command(command)

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
def set_target_temp_command():
    # Send "COOLER" command to the controller
    set_temp_fromuser = int(set_temp_var_entry.get())
    command = "TTARGET=\r" + str(set_temp_fromuser)
    send_command(command)
    
# Function to update temperature display
def update_temperature_log():
    temperature = get_temperature_command()
    
    # Get current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Display temperature, date, and time in the text widget
    temperature_history_text.insert(tk.END, f"{current_datetime}\t    {temperature}\n")
    
    # Add temperature entry to the log
    temperature_log.append((current_datetime, temperature))
    
    # If the user is already viewing the end of the text widget, scroll to show the latest entry
    temperature_history_text.see(tk.END)
    
    # Schedule next update after the user-defined interval
    interval = query_interval * 1000  # Convert to milliseconds
    global job_id
    job_id = root.after(interval, update_temperature_log)

# Function to handle downloading temperature log
def download_temp_log():
    # Generate file name based on start and end timestamps
    start_timestamp = temperature_log[0][0].replace(" ", "_").replace(":", "-")
    end_timestamp = temperature_log[-1][0].replace(" ", "_").replace(":", "-")
    file_name = f"templog_{start_timestamp}_to_{end_timestamp}.txt"
    
    # Write temperature log entries to file
    with open(file_name, 'w') as file:
        for entry in temperature_log:
            file.write(f"{entry[0]}\t    {entry[1]}\n")

# Function to turn on cooler and start logging temperature with user-defined interval
def cooler_on():

    cooler_on_command()
    global query_interval, query_unit
    interval = int(query_interval_entry.get())
    unit = query_unit_combobox.get()
    
    # Convert unit to seconds
    if unit == "minutes":
        interval *= 60
    elif unit == "hours":
        interval *= 3600
    
    # Update query interval and unit
    query_interval = interval
    query_unit = unit
    
    # Start updating temperature display
    update_temperature_log()

# Function to turn on cooler and start logging temperature with user-defined interval
def cooler_off():
    
    root.after_cancel(job_id)
    temperature_log = []
    cooler_off_command()
    temperature_history_text.delete('1.0', tk.END)

    
    

# Create GUI window
root = tk.Tk()
root.title("APSERa Cryo Monitor")
root.geometry("1400x800")  # Set window size to 1400x800

# Set font to Arial and increase font size
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="Arial", size=12)

# Create left frame for user input
user_input_frame = tk.Frame(root)
user_input_frame.pack(side=tk.LEFT, fill=tk.BOTH)

# Create label for current temperature
current_temp_label = tk.Label(user_input_frame, text="Current Temperature: ", font=default_font)
current_temp_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

# Create a StringVar to update the label text
current_temp_var = tk.StringVar()
current_temp_value_label = tk.Label(user_input_frame, textvariable=current_temp_var, font=default_font)
current_temp_value_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")


# Create label and entry for query interval
query_interval_label = tk.Label(user_input_frame, text="Temp Query every: ", font=default_font)
query_interval_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

query_interval_entry = tk.Entry(user_input_frame, font=default_font, width=5)
query_interval_entry.insert(tk.END, "1")
query_interval_entry.grid(row=1, column=1, padx=5, pady=5)

# Create dropdown menu for query unit
query_unit_combobox = ttk.Combobox(user_input_frame, values=["seconds", "minutes", "hours"], font=default_font, width=10)
query_unit_combobox.current(0)
query_unit_combobox.grid(row=1, column=2, padx=5, pady=5)

# Create a StringVar to update the Target temperature
target_temp_var = tk.StringVar()
target_temp_var_label = tk.Label(user_input_frame, textvariable=target_temp_var, font=default_font)
target_temp_var_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

# Create a StringVar to set the Target temperature
set_temp_var = tk.Label(user_input_frame, text="Change Target temperature: ", font=default_font)
set_temp_var.grid(row=3, column=0, padx=5, pady=5, sticky="e")

set_temp_var_entry = tk.Entry(user_input_frame, font=default_font, width=5)
set_temp_var_entry.insert(tk.END, "77")
set_temp_var_entry.grid(row=3, column=1, padx=5, pady=5)

# Create a StringVar to update the cooler status
cooler_status_var = tk.StringVar()
cooler_status_var_label = tk.Label(user_input_frame, textvariable=cooler_status_var, font=default_font)
cooler_status_var_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

# Create button to stop cooler and temp logging
cooler_on_button = tk.Button(user_input_frame, text="START COOLER", command=cooler_on, font=default_font)
cooler_on_button.grid(row=4, column=3, padx=5, pady=5)

# Create button to start cooler and temp logging
cooler_off_button = tk.Button(user_input_frame, text="STOP COOLER", command=cooler_off, font=default_font)
cooler_off_button.grid(row=5, column=3, padx=5, pady=5)

# Create right frame for temperature display
temperature_display_frame = tk.Frame(root)
temperature_display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create label for temperature history
temperature_history_label = tk.Label(temperature_display_frame, text="Temperature Log", font=default_font)
temperature_history_label.pack()

# Create text widget to display temperature history with three columns: Date, Time, and Temperature
temperature_history_text = tk.Text(temperature_display_frame, height=20, width=40, font=default_font)
temperature_history_text.pack(expand=True, fill=tk.BOTH)

# Create headers for the text widget
temperature_history_text.insert(tk.END, "Date & Time\t                 Temperature\n")

# Create scrollbar for the text widget
scrollbar = tk.Scrollbar(temperature_display_frame, command=temperature_history_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure text widget to use scrollbar
temperature_history_text.config(yscrollcommand=scrollbar.set)

# Create button to download temperature log
download_button = tk.Button(root, text="Download Temp Log", command=download_temp_log)
download_button.pack(side=tk.BOTTOM, pady=10)

# Update current temperature label
current_temp_var.set(get_temperature_command() + ' K') 
cooler_status_var.set('COOLER STATUS: ' + get_cooler_status_command())

# Start the GUI event loop
root.mainloop()
