import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python view_rfi_data_csv.py <input_name>")
    sys.exit(1)

input_name = sys.argv[1]
csv_file_path = input_name + ".csv"
header_file_path = input_name + "_hdr"

# Check if the files exist
if not (os.path.isfile(csv_file_path) and os.path.isfile(header_file_path)):
    print("Files not found:", csv_file_path, header_file_path)
    sys.exit(1)

# Reading parameters from the header file
Start_frequency = None
Stop_frequency = None
Sweep_points = None
Sweep_time = None
Start_time = None

with open(header_file_path, "r") as f:
    for line in f:
        if line.startswith("Start frequency:"):
            Start_frequency = float(line.split(": ")[1].strip())
        elif line.startswith("Stop frequency:"):
            Stop_frequency = float(line.split(": ")[1].strip())
        elif line.startswith("Sweep points:"):
            Sweep_points = int(line.split(": ")[1].strip())
        elif line.startswith("Sweep time:"):
            Sweep_time = float(line.split(": ")[1].strip())
        elif line.startswith("Start time:"):
            Start_time = line.split(": ")[1].strip()


# Reading data from CSV file
rfi_df = pd.read_csv(csv_file_path, header=None)
rfi_data = np.array(rfi_df)

# Convert Start_time to seconds
# Assumption: Start_time format is HH,MM,SS
hr, min, sec = map(int, Start_time.split(','))
start_seconds = hr * 3600 + min * 60 + sec

# Generate time axis labels
time_labels = []
for i in range(len(rfi_data)):
    time_seconds = start_seconds + i * Sweep_time  # Assuming each data point takes Sweep_time
    hours = int((time_seconds // 3600) % 24)  # Ensure hours do not exceed 24
    minutes = int((time_seconds // 60) % 60)
    seconds = int(time_seconds % 60)
    new_time = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    timestamp = pd.to_datetime(new_time, format='%H:%M:%S').strftime('%H,%M,%S')  # Comma separated format
    time_labels.append(timestamp)

# Modify time labels to switch to the next hour after 59 minutes
for i in range(1, len(time_labels)):
    if time_labels[i].split(',')[1] == '00':  # If minutes part is 00
        if time_labels[i].split(',')[0] == time_labels[i-1].split(',')[0]:  # If hours part remains the same
            time_labels[i] = time_labels[i].split(',')[0] + ',' + time_labels[i].split(',')[1] + ',' + time_labels[i].split(',')[2]

# Sort the time labels to maintain order
time_labels_sorted = sorted(time_labels, key=lambda x: pd.to_datetime(x, format='%H,%M,%S'))

# Plotting waterfall plot
plt.figure(figsize=(12, 8))
plt.imshow(rfi_data, aspect='auto', vmax=-60, vmin=-90, cmap='inferno', extent=(Start_frequency, Stop_frequency, 0, len(rfi_data)),
           interpolation='none')
plt.colorbar(label='dBm')
plt.title(input_name + "_waterfall", fontsize=18)
plt.xlabel('Frequency(GHz)', fontsize=14)
plt.ylabel('Time', fontsize=14)

# Displaying only 8 labels on the y-axis
num_labels = 8
plt.yticks(np.linspace(0, len(rfi_data) - 1, num_labels, dtype=int), [time_labels_sorted[i] for i in np.linspace(0, len(rfi_data) - 1, num_labels, dtype=int)], fontsize=8)  # Set time labels and font size

plt.tight_layout()  # Adjust layout for better appearance
plt.savefig(input_name + "_waterfall.png")
plt.show()

# Plotting frequency median
frequency_median = np.median(rfi_data[:, 2:], axis=0)
plt.figure(figsize=(9, 6))
plt.plot(np.linspace(Start_frequency, Stop_frequency, len(frequency_median)), frequency_median, linewidth=0.5, label='Frequency Median')
plt.xlabel('Frequency [GHz]')
plt.ylabel('Intensity [dBm]')
plt.title(input_name + "_frequency_median")
plt.legend(loc='upper right')
plt.savefig(input_name + '_freq_med.png')
plt.show()

# Plotting time median
time_index = np.arange(len(rfi_data))
time_median = np.median(rfi_data[:, :], axis=1)
plt.figure(figsize=(9, 6))
plt.plot(time_index, time_median, linewidth=0.5, label='Time Median')
plt.xlabel('Time [s]')
plt.ylabel('Intensity [dBm]')
plt.title(input_name + "_time_median")

# Displaying only 8 labels on the x-axis
num_labels = 8
plt.xticks(np.linspace(0, len(rfi_data) - 1, num_labels, dtype=int), [time_labels_sorted[i] for i in np.linspace(0, len(rfi_data) - 1, num_labels, dtype=int)], rotation=90, fontsize=8)  

plt.legend(loc='upper right')
plt.savefig(input_name + '_time_med.png')
plt.show()


