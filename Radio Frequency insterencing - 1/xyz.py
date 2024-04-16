from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import os

app = Flask(__name__)

# Initial dataset
datasets = {}
current_dataset = None  # Initialize current_dataset globally
uploaded_image_path = os.path.join('uploads', 'Hdr.png')  # Update the path


# Reading parameters from GBD_hdr.txt file
Start_frequency = None
Stop_frequency = None
Sweep_points = None
Sweep_time = None
Start_time = None

with open("GBD_hdr.txt", "r") as f:
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


@app.route('/')
def index():
    return render_template('side.html')

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global datasets, current_dataset, uploaded_image_path
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = file.filename

    # Determine the folder to save the dataset based on the requirement
    folder_name = "Dataset"  # replace "condition" with your actual condition
    file.save(os.path.join(folder_name, filename))
    
    current_dataset = pd.read_csv(os.path.join(folder_name, filename))
    current_dataset = current_dataset.select_dtypes(include=['number'])
    
    datasets[filename] = current_dataset
    
    return jsonify({'success': 'Dataset uploaded successfully'})

@app.route('/remove_dataset', methods=['POST'])
def remove_dataset():
    global datasets
    
    filename = request.form.get('filename')
    
    if filename in datasets:
        del datasets[filename]
        return jsonify({'success': 'Dataset removed successfully'})
    else:
        return jsonify({'error': 'Dataset not found'})

@app.route('/download_dataset/<filename>')
def download_dataset(filename):
    # Check if the dataset exists
    if filename in datasets:
        # Assuming the dataset is in CSV format
        # Change the content type and headers as required for different file formats
        return send_from_directory('Dataset', filename, as_attachment=True)
    else:
        return jsonify({'error': 'Dataset not found'})

@app.route('/stream_data', methods=['POST'])
def stream_data():
    global current_dataset
    
    # Assuming the incoming data is in JSON format
    data = request.get_json()

    # Process incoming data and update the current dataset
    if current_dataset is None:
        current_dataset = pd.DataFrame(columns=data.keys())

    new_data = pd.DataFrame([data])
    current_dataset = pd.concat([current_dataset, new_data], ignore_index=True)
    
    return jsonify({'success': True})

@app.route('/visualize', methods=['GET'])
def visualize():
    global current_dataset

    if current_dataset is None or current_dataset.empty:
        return jsonify({'error': 'No data available'})

    try:

# Plotting waterfall plot
        f_start = Start_frequency
        f_stop = Stop_frequency
        f_sweep=Sweep_points
        f_sweep_time = Sweep_time


        rfi_data = np.array(current_dataset)

        heatmap_trace = go.Heatmap(z=rfi_data,
                                   colorscale='Inferno',
                                   zmin=-90,
                                   zmax=-60,
                                   x=np.linspace(f_start,f_stop, rfi_data.shape[1]),  # Adjust x-values here
                                   y=[i * 1  for i in range(rfi_data.shape[0])],
                                   )

        heatmap_layout = go.Layout(
                                   
                                   xaxis=dict(title='Frequency [GHz]'),
                                   yaxis=dict(title='Time [seconds]'),
                                   width=680,
                                   height=600
                                   )

        heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)

        heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        data_median = np.median(rfi_data[:, 2:], axis=0)

        median_trace = go.Scatter(y=data_median, x=np.linspace(0.5, 4.0, len(data_median)), mode='lines', hoverinfo='x+y')

        median_layout = go.Layout(
                                  
                                  xaxis_title='Frequency[GHz]',
                                  yaxis_title='Median Intensity [dBm]',
                                  hovermode='closest',
                                  margin=dict(t=2),
                                  width=720,
                                  height=600
                                  )

        median_fig = go.Figure(data=[median_trace], layout=median_layout)

        median_graphJSON = json.dumps(median_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        time_index = np.arange(np.shape(rfi_data)[0])
        time_median = np.median(rfi_data[:,:], axis=1)

        time_median_trace = go.Scatter(x=time_median, y=time_index, mode='lines', name='Median Line')

        time_median_layout = go.Layout(
            
            xaxis_title='Intensity [dBm]',
            yaxis_title='Time [s]',
            hovermode='closest',
            showlegend=True,
            width=700,
            height=600
        )

        time_median_fig = go.Figure(data=[time_median_trace], layout=time_median_layout)
        time_median_graphJSON = json.dumps(time_median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify({'success': True, 'heatmap_graphJSON': heatmap_graphJSON, 'median_graphJSON': median_graphJSON, 'time_median_graphJSON': time_median_graphJSON, 'image_path': uploaded_image_path})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/uploads/<path:filename>')  # Serve the image
def download_file(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    app.run(debug=True)
