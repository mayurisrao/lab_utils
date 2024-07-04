import numpy as np
import plotly.graph_objects as go
import pandas as pd

# Set the filename without extension
filename = "Test_dataset_RFI_GUI_hdr"

# Construct the filename with extension
filename_with_extension = filename + ".csv"

# Read the CSV file using pandas
rfi_df = pd.read_csv(filename_with_extension, header=None)
rfi_data = np.array(rfi_df)

# Calculate median
time_index = np.arange(np.shape(rfi_data)[0])
time_median = np.median(rfi_data[:,:], axis=1)

# Create Plotly figure for median plot
fig_median = go.Figure(data=go.Scatter(x=time_median, y=time_index, mode='lines', name='Median Line'))

# Update layout
fig_median.update_layout(
    title=filename + '_time_median',
    xaxis_title='intensity [dBm]',
    yaxis_title='time [s]',
    hovermode='closest',  # Display values of nearest data point on hover
    showlegend=True
)

# Show the interactive median plot
fig_median.show()
