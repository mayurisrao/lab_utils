import tkinter as tk
from tkinter import filedialog
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt  # Importing matplotlib for median plot

# Function to load data from a file
def load_and_visualize_data():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            rfi_df = pd.read_csv(file_path, header=None)
            rfi_data = np.array(rfi_df)
            visualize_data(rfi_data, file_path)
            status_label.config(text="Data loaded successfully.", fg="green")
        except Exception as e:
            status_label.config(text=f"Error loading data: {e}", fg="red")

# Function to visualize data as an interactive waterfall chart and median plot
def visualize_data(data, file_path):
    filename = file_path.split('/')[-1].split('.')[0]  # Extracting filename without extension

    # Interactive waterfall plot using Plotly
    fig = go.Figure()

    fig.add_trace(go.Heatmap(z=data,
                             colorscale='inferno',
                             zmin=-90,
                             zmax=-60,
                             colorbar=dict(title='dBm'),
                             y=np.arange(0, len(data)),
                             x=np.linspace(0.5, 4.0, len(data[0])),
                             hoverongaps=False,
                             hoverinfo="z",
                             showscale=True))

    fig.update_layout(title=filename,
                      xaxis_title='Frequency(GHz)',
                      yaxis_title='time(seconds x 2)',
                      xaxis=dict(tickvals=np.linspace(0.5, 4.0, len(data[0]))),
                      yaxis=dict(tickvals=np.arange(0, len(data))),
                      height=700,
                      width=1000)

    # Save the interactive plot as an HTML file
    fout1 = filename + "_waterfall_interactive.html"
    fig.write_html(fout1)

    # Display the interactive waterfall plot
    fig.show()

    # Median plot
    data_median = np.median(data[:, 2:], axis=0)
    plt.figure(figsize=(12, 8))
    plt.plot(np.linspace(0.5, 4.0, len(data_median)), data_median, linewidth=0.5)
    plt.grid()
    plt.xlabel('Frequency(GHz)')
    plt.ylabel('Intensity (dBm)')
    plt.title('Median Plot')
    plt.tight_layout()

    fout2 = filename + '_med.png'
    plt.savefig(fout2)
    plt.show()

# GUI setup
root = tk.Tk()
root.title("Data Visualization Dashboard")

# Load Button
load_button = tk.Button(root, text="Load Data", command=load_and_visualize_data)
load_button.pack(pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="black")
status_label.pack()

root.mainloop()
