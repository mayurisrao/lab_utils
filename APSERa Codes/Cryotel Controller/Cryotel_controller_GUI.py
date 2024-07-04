#Vers ~ 1.1

import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import serial
from datetime import datetime

port = 'COM3'
ser_connection_fail = False  # Initialize ser_connection_fail outside the try block



#global declaration
global query_interval
global query_unit
global temperature_log

query_interval = 1
temperature_log = []



# Initialize serial connection
try:
    ser = serial.Serial(port, baudrate=9600, timeout=1)
except:
    ser_connection_fail = True

# # Function to send command and receive response
# def send_command(command):
#     if ser_connection_fail:
#         return 'NA'
#     else:    
#         ser.write(command.encode('utf-8'))
#         response = ''
#         while True:
#             line = ser.readline().decode('utf-8').strip()
#             if line == '':
#                 break
#             response += line + '\n'
#         return str(response.split('\n')[1])



# Initialize a flag variable to toggle between 'NA' and 'NA.'
alternate = False

def send_command(command):
    global alternate
    
    if ser_connection_fail:
        if command == "TC\r":
            alternate = not alternate
            if alternate:
                return 'NA'
            else:
                return 'NA !'
        else:
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
def get_sensor():
    # Send "TC" command to the controller
    command = "SENSOR\r"
    sensor = send_command(command)
    
    return sensor
    
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
    set_target_temp_fromuser = int(target_temp_entry.get())
    command = "TTARGET=" + str(set_target_temp_fromuser) + "\r"
    send_command(command)

def get_kp_ki_kd_command():
    command = "KP\r"
    kp = send_command(command)
    
    command = "KI=\r"
    ki = send_command(command)

    command = "KD=\r"
    kd = send_command(command)

    return_kpid = '  Kp: ' + str(kp) + '       Ki: ' + str(ki) + '       Kd: ' + str(kd)
    return return_kpid
def set_kp_ki_kd_command():
    kp_fromuser = float(kp_entry.get())
    command = "KP=" + str(kp_fromuser) + "\r"
    send_command(command)
    
    ki_fromuser = float(ki_entry.get())
    command = "KI=" + str(ki_fromuser) + "\r"
    send_command(command)

    kd_fromuser = float(kd_entry.get())
    command = "KD=" + str(kd_fromuser) + "\r"
    send_command(command)

    return_kpid = '  Kp: ' + str(kp_fromuser) + '       Ki: ' + str(ki_fromuser) + '       Kd: ' + str(kd_fromuser)
    current_pid_var.set(return_kpid)


def header_maker():
    # Write temperature log entries to file
    start_timestamp = temperature_log[0][0].replace(" ", "_").replace(":", "-")
    end_timestamp = temperature_log[-1][0].replace(" ", "_").replace(":", "-")
    file_name = f"header_{start_timestamp}_to_{end_timestamp}.txt"
    
    with open(file_name, 'w') as file:
        file.write(f"Date and Time: {temperature_log[0][0]} IST\n")
        duration = datetime.strptime(temperature_log[-1][0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(temperature_log[0][0], "%Y-%m-%d %H:%M:%S")
        file.write(f"Duration: {duration}\n")
        
        file.write(f"Temperature at Exit: {get_temperature_command()}\n")
        file.write(f"Target Temperature at Exit: {get_target_temp_command()}\n")
        file.write(f"PID Values (Kp, Ki, Kd): {get_kp_ki_kd_command()}\n")
        file.write(f"Sensor: {get_sensor()}\n")
        
# functions to overwrite the logging interval
def load_query_interval():
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
    current_query_interval_var.set(str(query_interval) + ' s')


# Function to handle downloading temperature log
def download_temp_log():
    global temperature_log
    # Generate file name based on start and end timestamps
    try:    
        start_timestamp = temperature_log[0][0].replace(" ", "_").replace(":", "-")
        end_timestamp = temperature_log[-1][0].replace(" ", "_").replace(":", "-")
        file_name = f"templog_{start_timestamp}_to_{end_timestamp}.txt"
        
        # Write temperature log entries to file
        with open(file_name, 'w') as file:
            for entry in temperature_log:
                file.write(f"{entry[0]}\t    {entry[1]}\n")
    except:
        pass
        
    header_maker()
        
#function to update target temp
def target_temp_update():
    set_target_temp_command()
    current_target_temp_var.set(str(target_temp_entry.get()) + ' K')

def refresh_target_temp():
    current_target_temp_var.set(str(get_target_temp_command()) + ' K')

def refresh_pid():
    current_pid_var.set(str(get_kp_ki_kd_command()))
    
def start_cooler():
    stop_cooler_button.config(state=tk.NORMAL)
    stop_time = (auto_off_entry.get())
    cooler_on_command()
    
    if stop_time == 'off':
        pass
    else:        
        root.after(int(stop_time)*1000, stop_cooler)
    update_temperature_log()
    start_cooler_button.config(state=tk.DISABLED)

def stop_cooler():    
    global temperature_log
    start_cooler_button.config(state=tk.NORMAL)
    download_temp_log()
    
    cooler_off_command()
    temperature_log = []
    
    temperature_history_text.delete('1.0', tk.END)
    root.after_cancel(job_id)
    # Create headers for the text widget
    temperature_history_text.insert(tk.END, "Date & Time\t                 Temperature\n")
    stop_cooler_button.config(state=tk.DISABLED)
    
# Function to update temperature display
def update_temperature_log():
    global temperature_log
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
    global job_id
    job_id = root.after(query_interval * 1000, update_temperature_log)
    
def track_system_parameters():
    currenttemp = get_temperature_command()
    current_temp_var.set(currenttemp)

    cooler_status_var.set(get_cooler_status_command())
    
    root.after(5000, track_system_parameters)

   

# Create GUI window
root = tk.Tk()
root.title("APSERa Cryo Monitor")
root.geometry("1400x800")  # Set window size to 1400x800

# Set font to Arial and increase font size
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="Arial", size=11)


# Create left frame for user input
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH)



# Create label for current temperature
current_temp_label = tk.Label(left_frame, text="Current Temperature: ", font=default_font)
current_temp_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
# Create a StringVar to update the current temp
current_temp_var = tk.StringVar()
current_temp_value_label = tk.Label(left_frame, textvariable=current_temp_var, font=default_font)
current_temp_value_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")



# Create label for query interval
query_interval_label = tk.Label(left_frame, text="Temp Query every: ", font=default_font)
query_interval_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
# Create entry for query interval
query_interval_entry = tk.Entry(left_frame, font=default_font, width=5)
query_interval_entry.insert(tk.END, "1")
query_interval_entry.grid(row=1, column=1, padx=5, pady=5)
# Create dropdown menu for query unit
query_unit_combobox = ttk.Combobox(left_frame, values=["seconds", "minutes", "hours"], font=default_font, width=10)
query_unit_combobox.current(0)
query_unit_combobox.grid(row=1, column=2, padx=5, pady=5)
# Create button to load query interval for data logging
load_query_interval_button = tk.Button(left_frame, text="Update log interval", command=load_query_interval, font=default_font)
load_query_interval_button.grid(row=1, column=3, padx=5, pady=5)
# Create label for current query interval
query_interval_label = tk.Label(left_frame, text="Current: ", font=default_font)
query_interval_label.grid(row=1, column=4, padx=5, pady=5, sticky="e")
# Create a StringVar to update the target temp
current_query_interval_var = tk.StringVar()
current_query_interval_label = tk.Label(left_frame, textvariable=current_query_interval_var, font=default_font)
current_query_interval_label.grid(row=1, column=5, padx=5, pady=5, sticky="w")



# Create label for target temperature
target_temp_label = tk.Label(left_frame, text="Set Target Temperature: ", font=default_font)
target_temp_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
# Create entry for target temperature
target_temp_entry = tk.Entry(left_frame, font=default_font, width=5)
target_temp_entry.insert(tk.END, "280")
target_temp_entry.grid(row=2, column=1, padx=5, pady=5)
# Create button to load target temperature
target_temp_button = tk.Button(left_frame, text="Update target temp", command=target_temp_update, font=default_font)
target_temp_button.grid(row=2, column=3, padx=5, pady=5)
# Create label for current target temp display
target_temp_label = tk.Label(left_frame, text="Current: ", font=default_font)
target_temp_label.grid(row=2, column=4, padx=5, pady=5, sticky="e")
# Create a StringVar for target temp current display
current_target_temp_var = tk.StringVar()
current_target_temp_value_label = tk.Label(left_frame, textvariable=current_target_temp_var, font=default_font)
current_target_temp_value_label.grid(row=2, column=5, padx=5, pady=5, sticky="w")
# Create button to load target temperature
refresh_target_temp_button = tk.Button(left_frame, text="Refresh", command=refresh_target_temp, font=default_font)
refresh_target_temp_button.grid(row=2, column=6, padx=5, pady=5)



# Create label for pid values
pid_label = tk.Label(left_frame, text="Set PID (Kp, Ki, Kd):  ", font=default_font)
pid_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
# Create entry for kp values
kp_entry = tk.Entry(left_frame, font=default_font, width=5)
kp_entry.insert(tk.END, "1")
kp_entry.grid(row=3, column=1, padx=5, pady=5)
# Create entry for ki values
ki_entry = tk.Entry(left_frame, font=default_font, width=5)
ki_entry.insert(tk.END, "1")
ki_entry.grid(row=4, column=1, padx=5, pady=5)
# Create entry for kd values
kd_entry = tk.Entry(left_frame, font=default_font, width=5)
kd_entry.insert(tk.END, "1")
kd_entry.grid(row=5, column=1, padx=5, pady=5)
# Create button to load pid values
pid_load_button = tk.Button(left_frame, text="Update PID", command=set_kp_ki_kd_command, font=default_font)
pid_load_button.grid(row=3, column=2, padx=5, pady=5)
# Create label for current target temp display
current_pid_label = tk.Label(left_frame, text="Current: ", font=default_font)
current_pid_label.grid(row=3, column=3, padx=5, pady=5, sticky="e")
# Create a StringVar for target temp current display
current_pid_var = tk.StringVar()
current_pid_var_label = tk.Label(left_frame, textvariable=current_pid_var, font=default_font)
current_pid_var_label.grid(row=3, column=4, padx=5, pady=5, sticky="w")
# Create button to load target temperature
refresh_pid_button = tk.Button(left_frame, text="Refresh", command=refresh_pid, font=default_font)
refresh_pid_button.grid(row=3, column=5, padx=5, pady=5)



# Create label for auto off
auto_off_label = tk.Label(left_frame, text="Auto OFF:  ", font=default_font)
auto_off_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
# Create entry for auto off
auto_off_entry = tk.Entry(left_frame, font=default_font, width=5)
auto_off_entry.insert(tk.END, "off")
auto_off_entry.grid(row=6, column=1, padx=5, pady=5)
# Create button to start cooler
start_cooler_button = tk.Button(left_frame, text="Start Cooler", command=start_cooler, font=default_font)
start_cooler_button.grid(row=8, column=0, padx=5, pady=5)
# Create button to stop cooler
stop_cooler_button = tk.Button(left_frame, text="Stop Cooler", command=stop_cooler, font=default_font)
stop_cooler_button.grid(row=8, column=1, padx=5, pady=5)
# Create label for current target temp display
cooler_status_label = tk.Label(left_frame, text="Cooler Status: ", font=default_font)
cooler_status_label.grid(row=8, column=2, padx=5, pady=5, sticky="e")
# Create a StringVar for target temp current display
cooler_status_var = tk.StringVar()
cooler_status_var_label = tk.Label(left_frame, textvariable=cooler_status_var, font=default_font)
cooler_status_var_label.grid(row=8, column=3, padx=5, pady=5, sticky="w")








# Create right frame for temperature display ==============================================================================
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create label for temperature history
temperature_history_label = tk.Label(right_frame, text="Temperature Log", font=default_font)
temperature_history_label.pack()

# Create text widget to display temperature history with three columns: Date, Time, and Temperature
temperature_history_text = tk.Text(right_frame, height=20, width=40, font=default_font)
temperature_history_text.pack(expand=True, fill=tk.BOTH)

# Create headers for the text widget
temperature_history_text.insert(tk.END, "Date & Time\t                 Temperature\n")

# Create scrollbar for the text widget
scrollbar = tk.Scrollbar(right_frame, command=temperature_history_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure text widget to use scrollbar
temperature_history_text.config(yscrollcommand=scrollbar.set)

# Create button to download temperature log
download_button = tk.Button(right_frame, text="Download Temp Log", command=download_temp_log)
download_button.pack(side=tk.BOTTOM, pady=10)



#default initial functions to run
load_query_interval()
target_temp_update()


#initiate repeat functions to run
root.after(5000, track_system_parameters) 
# Start the GUI event loop
root.mainloop()
