import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Set the filename without extension
filename = "Test_data_set_RFI_GUI"

# Construct the filename with extension
filename_with_extension = filename + ".csv"
fout1 = filename + "_waterfall.png"
fout2 = filename + '_med.png'

# Read the CSV file using pandas
rfi_df = pd.read_csv(filename_with_extension, header=None)
rfi_data = np.array(rfi_df)

# Plot the waterfall plot
plt.figure(figsize=(9, 15))
plt.imshow(rfi_data, aspect='auto', vmax=-60, vmin=-90, cmap='inferno', extent=(0.5, 4.0, 0, len(rfi_data)), interpolation='none')
plt.grid(c='w')
plt.colorbar(label='dBm')
plt.title(filename)
plt.xlabel('Frequency(GHz)')
plt.ylabel('time(seconds x 2)')
plt.savefig(fout1)
plt.show()

# Calculate and plot the median
data_median = np.median(rfi_data[:, 2:], axis=0)
plt.figure(figsize=(9, 15))
plt.rcParams.update({'font.size': 10})
plt.plot(np.linspace(0.5, 4.0, len(data_median)), data_median, linewidth=0.5)
plt.grid()
plt.xlabel('frequency(GHz)')
plt.ylabel('intensity (dBm)')
plt.title(filename)
plt.legend(loc='upper right')
plt.savefig(fout2)
plt.show()
