import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import serial
import time

# Initialize global variables
ser = None
terminator = '\r\n'
read_timeout = 1

def connect_serial():
    global ser
    port = port_entry.get().strip() or "/dev/ttyUSB3"
    baudrate = baudrate_entry.get().strip() or "9600"

    try:
        ser = serial.Serial(
            port=port,
            baudrate=int(baudrate),
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        messagebox.showinfo("Info", "Serial Communication SUCCESS")
    except Exception as e:
        messagebox.showerror("Error", f"Serial Communication FAILED: {e}")

def read_response():
    start_time = time.time()
    response = ""

    while (time.time() - start_time) < read_timeout:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode()
            response += data
            if terminator in response:
                response = response.split(terminator, 1)[0]
                return response

    return "No response received within timeout period"

def execute_command():
    if not ser:
        messagebox.showerror("Error", "Not connected to serial port.")
        return

    command = command_text.get("1.0", tk.END).strip()
    if not command:
        messagebox.showerror("Error", "No command entered.")
        return

    try:
        ser.write((command + terminator).encode())
        response = read_response()
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, response)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute command: {e}")

def clear_result():
    result_text.delete("1.0", tk.END)

def curve_delete():
    curve = simpledialog.askstring("Input", "Enter curve number to delete:")
    if curve is None:
        return
    cmd = f'CRVDEL {curve}'
    try:
        ser.write((cmd + terminator).encode())
        messagebox.showinfo("Info", f'Curve {curve} has been deleted from datalogger')
    except Exception as e:
        messagebox.showerror("Error", f'Failed to delete curve: {e}')

def curve_set():
    curve = simpledialog.askstring("Input", "Which curve to configure:")
    name = simpledialog.askstring("Input", "Give curve name (max 15 char):")
    SN = simpledialog.askstring("Input", "Give Serial number (max 10 char):")
    format_ = simpledialog.askstring("Input", "Curve data format? 2 = V/K, 3 = Ohm/K, 4 = log Ohm/K:")
    limitvalue_temp = simpledialog.askstring("Input", "Curve temperature limit in Kelvin:")
    coef = simpledialog.askstring("Input", "Curve temperature coefficient. 1 = negative, 2 = positive:")

    if None in (curve, name, SN, format_, limitvalue_temp, coef):
        return

    cmd = f'CRVHDR {curve}, {name}, {SN}, {format_}, {limitvalue_temp}, {coef}'
    try:
        ser.write((cmd + terminator).encode())
        messagebox.showinfo("Info", f'Curve Header created for Curve {curve}')
    except Exception as e:
        messagebox.showerror("Error", f'Failed to set curve header: {e}')

def curve_queryheader_single():
    curve = simpledialog.askstring("Input", "Which curve to query:")
    if curve is None:
        return
    cmd = f'CRVHDR? {curve}'
    try:
        ser.write((cmd + terminator).encode())
        response = read_response()
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, response)
    except Exception as e:
        messagebox.showerror("Error", f'Failed to query curve header: {e}')

def curve_entire_read():
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not filename:
        return
    curve = simpledialog.askstring("Input", "Which curve data points to save:")
    if curve is None:
        return
    with open(filename, 'w') as file:
        i = 0
        while True:
            cmd = f'CRVPT? {curve} {i}'
            ser.write((cmd + terminator).encode())
            response = read_response()
            if response == "+0.00000,+00.0000" and i != 0:
                break
            file.write(response + '\n')  # Write the response to the file
            i += 1
            time.sleep(0.1)
            
    messagebox.showinfo("Info", f"Data has been saved to {filename}")

def curve_queryheader_all():
    curve_index_list = list(range(1,10)) + list(range(21,29))

    curve_list = ""
    for i in curve_index_list:
        cmd = f'CRVHDR? {i}'
        try:
            ser.write((cmd + terminator).encode())
            response = read_response()
            curve_list += f'Curve {i}: {response}\n'
        except Exception as e:
            messagebox.showerror("Error", f'Failed to query curve header {i}: {e}')
            break
        time.sleep(0.1)
        
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, curve_list)

def curve_point_read():
    curve = simpledialog.askstring("Input", "Which curve to read:")
    index = simpledialog.askstring("Input", "Index:")

    if curve is None or index is None:
        return

    cmd = f'CRVPT? {curve}, {index}'
    try:
        ser.write((cmd + terminator).encode())
        response = read_response()
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, response)
    except Exception as e:
        messagebox.showerror("Error", f'Failed to read curve point: {e}')

def load_curve():
    filelocation = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not filelocation:
        return
    data = load_curvedata_fromfile(filelocation)

    curve = simpledialog.askstring("Input", "Which curve to load to:")
    if curve is None:
        return

    for i in range(len(data)):
        curve_point_set(str(curve), str(i), str(data[i][1]), str(data[i][0]))
        time.sleep(0.1)

    messagebox.showinfo("Info", 'Curve loaded')

def curve_point_set(curve, index, units_value, temp_value):
    cmd = f'CRVPT {curve}, {index}, {units_value}, {temp_value}'
    try:
        ser.write((cmd + terminator).encode())
    except Exception as e:
        messagebox.showerror("Error", f'Failed to set curve point: {e}')

def load_curvedata_fromfile(file_location):
    data_list = []
    with open(file_location, 'r') as file:
        for line in file:
            values = line.strip().split()
            data_list.append([float(value) for value in values])
    return data_list[::-1]

# Create the main window
root = tk.Tk()
root.title("Curve Handling Interface")

# Serial Port Configuration
tk.Label(root, text="Port:").grid(row=0, column=0)
port_entry = tk.Entry(root)
port_entry.grid(row=0, column=1)

tk.Label(root, text="Baudrate:").grid(row=1, column=0)
baudrate_entry = tk.Entry(root)
baudrate_entry.grid(row=1, column=1)

connect_button = tk.Button(root, text="Connect", command=connect_serial)
connect_button.grid(row=2, column=0, columnspan=2)

# Command Section
tk.Label(root, text="Command:").grid(row=3, column=0, columnspan=2)
command_text = tk.Text(root, height=5, width=50)
command_text.grid(row=4, column=0, columnspan=2)

execute_button = tk.Button(root, text="Execute", command=execute_command)
execute_button.grid(row=5, column=0, columnspan=2)

# Result Section
tk.Label(root, text="Result:").grid(row=6, column=0, columnspan=2)
result_text = tk.Text(root, height=10, width=50)
result_text.grid(row=7, column=0, columnspan=2)

clear_button = tk.Button(root, text="Clear", command=clear_result)
clear_button.grid(row=8, column=0, columnspan=2)

# Function Buttons
curve_delete_button = tk.Button(root, text="Delete Curve", command=curve_delete)
curve_delete_button.grid(row=9, column=0, columnspan=2)

curve_set_button = tk.Button(root, text="Set Curve Header", command=curve_set)
curve_set_button.grid(row=10, column=0, columnspan=2)

query_header_button = tk.Button(root, text="Query Header (Single)", command=curve_queryheader_single)
query_header_button.grid(row=11, column=0, columnspan=2)

query_all_button = tk.Button(root, text="Query All Headers", command=curve_queryheader_all)
query_all_button.grid(row=12, column=0, columnspan=2)

read_entire_button = tk.Button(root, text="Read Entire Curve", command=curve_entire_read)
read_entire_button.grid(row=13, column=0, columnspan=2)

read_point_button = tk.Button(root, text="Read Curve Point", command=curve_point_read)
read_point_button.grid(row=14, column=0, columnspan=2)

load_curve_button = tk.Button(root, text="Load Curve", command=load_curve)
load_curve_button.grid(row=15, column=0, columnspan=2)

# Start the GUI event loop
root.mainloop()
