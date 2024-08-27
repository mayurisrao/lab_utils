import tkinter as tk
from tkinter import messagebox, ttk
import serial
import time

# Global variables
ser = None
terminator = '\r\n'
read_timeout = 2

def initialize_serial(port, baudrate):
    try:
        return serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to initialize serial port: {e}")
        return None

def read_response(serial_port, timeout_period, terminator):
    start_time = time.time()
    response = ""
    
    while (time.time() - start_time) < timeout_period:
        if serial_port.in_waiting > 0:
            data = serial_port.read(serial_port.in_waiting).decode()
            response += data
            
            if terminator in response:
                response = response.split(terminator, 1)[0]
                return response
    
    return None

def remote_on():
    cmd = 'CH 1'
    cmd += terminator
    ser.write(cmd.encode())

def remote_off():
    cmd = 'exit'
    cmd += terminator
    ser.write(cmd.encode())

def get_voltage_current():
    cmd = 'SO:VO?'
    cmd += terminator
    ser.write(cmd.encode())
    voltage = read_response(ser, read_timeout, terminator)
    
    cmd = 'SO:CU?'
    cmd += terminator
    ser.write(cmd.encode())
    current = read_response(ser, read_timeout, terminator)

    return voltage, current

def set_voltage_current():
    voltage = voltage_entry.get()
    current = current_entry.get()
    cmd = f'SO:VO {voltage}'
    cmd += terminator
    ser.write(cmd.encode())
    cmd = f'SO:CU {current}'
    cmd += terminator
    ser.write(cmd.encode())
    messagebox.showinfo("Info", "Voltage and current set successfully")

def update_voltage_current():
    voltage, current = get_voltage_current()
    if voltage and current:
        voltage_label.config(text=voltage)
        current_label.config(text=current)
    root.after(2000, update_voltage_current)

def setup_serial():
    global ser
    port = port_entry.get()
    baudrate = int(baudrate_entry.get())

    ser = initialize_serial(port, baudrate)
    if ser:
        remote_on()
        update_voltage_current()
    else:
        messagebox.showerror("Error", "Failed to connect to serial port")

def on_closing():
    if ser:
        remote_off()
    root.destroy()

# Create main window
root = tk.Tk()
root.title("Power Supply Control")
root.geometry("350x300")
root.configure(bg='#f0f0f0')

# Styling
style = ttk.Style()
style.configure('TButton', font=('Arial', 10), padding=6)
style.configure('TLabel', font=('Arial', 10), background='#f0f0f0')
style.configure('TEntry', font=('Arial', 10))

# Setup Widgets
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

tk.Label(frame, text="Port:", background='#f0f0f0').grid(row=0, column=0, sticky=tk.W, pady=5)
port_entry = ttk.Entry(frame)
port_entry.grid(row=0, column=1, pady=5)
port_entry.insert(0, "COM7")

tk.Label(frame, text="Baudrate:", background='#f0f0f0').grid(row=1, column=0, sticky=tk.W, pady=5)
baudrate_entry = ttk.Entry(frame)
baudrate_entry.grid(row=1, column=1, pady=5)
baudrate_entry.insert(0, "9600")

connect_button = ttk.Button(frame, text="Connect", command=setup_serial)
connect_button.grid(row=2, column=0, columnspan=2, pady=10)

tk.Label(frame, text="Voltage:", background='#f0f0f0').grid(row=3, column=0, sticky=tk.W, pady=5)
voltage_label = ttk.Label(frame, text="0.0")
voltage_label.grid(row=3, column=1, pady=5)

tk.Label(frame, text="Current:", background='#f0f0f0').grid(row=4, column=0, sticky=tk.W, pady=5)
current_label = ttk.Label(frame, text="0.0")
current_label.grid(row=4, column=1, pady=5)

tk.Label(frame, text="Set Voltage:", background='#f0f0f0').grid(row=5, column=0, sticky=tk.W, pady=5)
voltage_entry = ttk.Entry(frame)
voltage_entry.grid(row=5, column=1, pady=5)

tk.Label(frame, text="Set Current:", background='#f0f0f0').grid(row=6, column=0, sticky=tk.W, pady=5)
current_entry = ttk.Entry(frame)
current_entry.grid(row=6, column=1, pady=5)

accept_button = ttk.Button(frame, text="Accept", command=set_voltage_current)
accept_button.grid(row=7, column=0, columnspan=2, pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
