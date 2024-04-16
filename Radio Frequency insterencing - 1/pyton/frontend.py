import tkinter as tk
from tkinter import filedialog
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class RFIMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radio Frequency Interference Monitor")
        self.root.geometry("800x600")

        # Navbar
        self.navbar_frame = tk.Frame(self.root, bg="#e3f2fd")
        self.navbar_frame.pack(fill=tk.X)

        self.loadDataset_btn = tk.Button(self.navbar_frame, text="Load Dataset", command=self.uploadDataset)
        self.loadDataset_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.runVisualization_btn = tk.Button(self.navbar_frame, text="Run Visualization", command=self.runVisualization, state=tk.DISABLED)
        self.runVisualization_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Status label
        self.status_label = tk.Label(self.root, fg="red")
        self.status_label.pack()

        # Matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def uploadDataset(self):
        filename = filedialog.askopenfilename(title="Select File")
        if filename:
            self.status_label.config(text=f"File {filename} loaded successfully")
            self.runVisualization_btn.config(state=tk.NORMAL)
            self.dataset = pd.read_csv(filename)

    def runVisualization(self):
        if not hasattr(self, 'dataset'):
            self.status_label.config(text="Error: No dataset loaded")
            return

        self.ax.clear()
        # Perform visualization using Matplotlib
        self.dataset.plot(ax=self.ax)
        self.ax.set_title('Visualization')
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = RFIMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
