from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import os

app = Flask(__name__)

# Initial dataset file
current_dataset = pd.DataFrame()

# Create directories if they don't exist
if not os.path.exists('csv_files'):
    os.makedirs('csv_files')

if not os.path.exists('hdr_files'):
    os.makedirs('hdr_files')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_hdr_file():
    hdr_content = request.json['hdrContent']
    filename = request.json['filename']  # Extract filename from request

    # Save HDR content to a file with the same name provided by the user
    with open(f'hdr_files/{filename}', 'w') as f:
        f.write(hdr_content)

    return jsonify({'success': True})

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global current_dataset
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save the uploaded file to the server
    filename = os.path.join('csv_files', file.filename)
    file.save(filename)
    
    # Replace the current dataset with the uploaded file
    current_dataset = pd.read_csv(filename)
    
    # Handle non-numeric data: Drop non-numeric columns
    current_dataset = current_dataset.select_dtypes(include=['number'])
    
    # Send success message to frontend
    return jsonify({'success': 'Dataset ' + filename + ' uploaded successfully'})

@app.route('/visualize', methods=['POST'])
def visualize():
    global current_dataset
    
    # Check if dataset is loaded
    if current_dataset.empty:
        return jsonify({'error': 'No dataset loaded'})

    try:
        # Generate the waterfall heatmap    
        rfi_data = np.array(current_dataset)

        # Reading parameters from the header file
        Start_frequency = None
        Stop_frequency = None
        Sweep_points = None
        Sweep_time = None
        Start_time = None

        # Reading frequency and time metadata
        hdr_content = request.json['hdrContent']
        lines = hdr_content.split('\n')
        for line in lines:
            if line.startswith("Start frequency:"):
                Start_frequency = float(line.split(": ")[1].strip()) / 1e9  # Convert to GHz
            elif line.startswith("Stop frequency:"):
                Stop_frequency = float(line.split(": ")[1].strip()) / 1e9  # Convert to GHz
            elif line.startswith("Sweep points:"):
                Sweep_points = int(line.split(": ")[1].strip())
            elif line.startswith("Sweep time:"):
                Sweep_time = float(line.split(": ")[1].strip())
            elif line.startswith("Start time:"):
                Start_time = line.split(": ")[1].strip()

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
            time_labels.append(new_time)

        # Plotting waterfall plot
        f_start = Start_frequency
        f_stop = Stop_frequency
        f_sweep = Sweep_points
        f_sweep_time = Sweep_time

        # Create the heatmap trace
        heatmap_trace = go.Heatmap( 
                                   
                                   z=rfi_data,
                                   colorscale='Inferno',
                                   zmin=-90,
                                   zmax=-60,
                                   x=np.linspace(f_start, f_stop, f_sweep),
                                   y=time_labels
                                   )

        heatmap_layout = go.Layout(
                                   xaxis=dict(title='Frequency [GHz]'),
                                   yaxis=dict(title='Time'),
                                   width=700,
                                   height=600
                                   )

        heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)

        heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Calculate median line
        data_median = np.median(rfi_data[:, 2:], axis=0)

        median_trace = go.Scatter(y=data_median, x=np.linspace(Start_frequency, Stop_frequency, len(data_median)), mode='lines', hoverinfo='x+y')

        median_layout = go.Layout(
                                  xaxis_title='Frequency [GHz]',
                                  yaxis_title='Median Intensity [dBm]',
                                  hovermode='closest',
                                  margin=dict(t=2),
                                  width=700,
                                  height=600
                                  )

        median_fig = go.Figure(data=[median_trace], layout=median_layout)

        median_graphJSON = json.dumps(median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Calculate median line
        time_index = np.arange(np.shape(rfi_data)[0])
        time_median = np.median(rfi_data[:,:], axis=1)

        # Plot median line with y-axis labeled with time_labels
        time_median_trace = go.Scatter(x=time_median, y=time_labels, mode='lines', name='Median Line')

        # Layout for the median line graph
        time_median_layout = go.Layout(
            xaxis_title='Intensity [dBm]',
            yaxis_title='Time',
            hovermode='closest',
            showlegend=True,
            width=700,
            height=600
        )

        # Create the median line figure
        time_median_fig = go.Figure(data=[time_median_trace], layout=time_median_layout)

        # Convert the figure to JSON
        time_median_graphJSON = json.dumps(time_median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify({'success': True, 
                        'heatmap_graphJSON': heatmap_graphJSON, 
                        'median_graphJSON': median_graphJSON, 
                        'time_median_graphJSON': time_median_graphJSON})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
