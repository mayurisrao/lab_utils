import numpy as np
import plotly.graph_objects as go
import pandas as pd

# Set the filename without extension
filename = "Test_data_set_RFI_GUI"

# Construct the filename with extension
filename_with_extension = filename + ".csv"
fout1 = filename + "_waterfall_interactive.html"
fout2 = filename + '_med.png'

# Read the CSV file using pandas
rfi_df = pd.read_csv(filename_with_extension, header=None)
rfi_data = np.array(rfi_df)

# Interactive waterfall plot using Plotly
fig = go.Figure()

fig.add_trace(go.Heatmap(z=rfi_data,
                         colorscale='inferno',
                         zmin=-90,
                         zmax=-60,
                         colorbar=dict(title='dBm'),
                         y=np.arange(0, len(rfi_data)),
                         x=np.linspace(0.5, 4.0, len(rfi_data[0])),
                         hoverongaps=False,
                         hoverinfo="z",
                         showscale=True))

fig.update_layout(title=filename,
                  xaxis_title='Frequency(GHz)',
                  yaxis_title='time(seconds x 2)',
                  xaxis=dict(tickvals=np.linspace(0.5, 4.0, len(rfi_data[0]))),
                  yaxis=dict(tickvals=np.arange(0, len(rfi_data))),
                  height=700,
                  width=1000)

# Save the interactive plot as an HTML file
fig.write_html(fout1)

# Display the interactive waterfall plot
fig.show()
