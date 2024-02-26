import numpy as np
import plotly.graph_objects as go
import pandas as pd

# Set the filename without extension
filename = "Test_data_set_RFI_GUI"

# Construct the filename with extension
filename_with_extension = filename + ".csv"

# Read the CSV file using pandas
rfi_df = pd.read_csv(filename_with_extension, header=None)
rfi_data = np.array(rfi_df)

# Calculate median
data_median = np.median(rfi_data[:, 2:], axis=0)

# Create Plotly figure for median plot
fig_median = go.Figure(data=go.Scatter(y=data_median, x=np.linspace(0.5, 4.0, len(data_median)), mode='lines', hoverinfo='x+y'))

# Update layout
fig_median.update_layout(
    title=filename + ' Median Plot',
    xaxis_title='Frequency(GHz)',
    yaxis_title='Median Intensity (dBm)',
    xaxis=dict(
        autorange="reversed",  # Reverse the x-axis
        type="linear"
    ),
    yaxis=dict(
        autorange="reversed",  # Reverse the y-axis
        type="linear"
    ),
    hovermode='closest'  # Display values of nearest data point on hover
)

# Show the interactive median plot
fig_median.show()
