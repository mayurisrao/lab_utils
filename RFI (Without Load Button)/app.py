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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global datasets, current_dataset
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = file.filename

    # Save the uploaded CSV file to the Dataset folder
    folder_name = "Dataset"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_path = os.path.join(folder_name, filename)
    file.save(file_path)
    
    # Load the CSV file
    current_dataset = pd.read_csv(file_path)
    current_dataset = current_dataset.select_dtypes(include=['number'])
    
    datasets[filename] = current_dataset
    
    # Check for the corresponding HDR or text file
    hdr_folder = "HDR"
    base_name = os.path.splitext(filename)[0]
    hdr_file_path = None
    for ext in ['_hdr', '.txt']:
        potential_path = os.path.join(hdr_folder, base_name + ext)
        if os.path.isfile(potential_path):
            hdr_file_path = potential_path
            break

    hdr_found = hdr_file_path is not None

    if hdr_found:
        with open(hdr_file_path, 'r') as f:
            hdr_content = f.read()
        return jsonify({'success': 'Dataset uploaded successfully', 'hdr_content': hdr_content, 'hdr_found': True})
    else:
        return jsonify({'success': 'Dataset uploaded successfully', 'hdr_content': 'Hdr File Not Found!!', 'hdr_found': False})

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

@app.route('/visualize', methods=['POST'])
def visualize():
    global current_dataset

    if current_dataset is None or current_dataset.empty:
        return jsonify({'error': 'No data available'})

    try:
        # Reading parameters from the header file
        Start_frequency = None
        Stop_frequency = None
        Sweep_points = None
        Sweep_time = None
        Start_time = None
        hdr_content = request.json.get('hdrContent', None)

        if hdr_content:
            # Read frequency and time metadata from the HDR content
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

        # If HDR content is not available, set default values for visualization
        if Start_frequency is None or Stop_frequency is None or Sweep_points is None or Sweep_time is None or Start_time is None:
            Start_frequency = 0
            Stop_frequency = 1
            Sweep_points = 1
            Sweep_time = 1
            Start_time = '00,00,00'

        # Convert Start_time to seconds
        hr, min, sec = map(int, Start_time.split(','))
        start_seconds = hr * 3600 + min * 60 + sec

        # Generate time axis labels
        time_labels = []
        for i in range(len(current_dataset)):
            time_seconds = start_seconds + i * Sweep_time  # Assuming each data point takes Sweep_time
            hours = int((time_seconds // 3600) % 24)  # Ensure hours do not exceed 24
            minutes = int((time_seconds // 60) % 60)
            seconds = int(time_seconds % 60)
            new_time = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
            timestamp = pd.to_datetime(new_time, format='%H:%M:%S').strftime('%H,%M,%S')  # Comma separated format
            time_labels.append(timestamp)

        # Synchronize time labels to the nearest second
        time_labels = sorted(list(set(time_labels)))

        # Ensure both plots use the same time labels
        common_time_labels = time_labels[:len(current_dataset)]

        # Plotting waterfall plot
        f_start = Start_frequency
        f_stop = Stop_frequency
        f_sweep = Sweep_points

        # Create the heatmap trace
        heatmap_trace = go.Heatmap(
            z=current_dataset.values,
            colorscale='Inferno',
            zmin=-90,
            zmax=-60,
            x=np.linspace(f_start, f_stop, f_sweep),
            y=common_time_labels
        )

        heatmap_layout = go.Layout(
            xaxis=dict(title='Frequency [GHz]'),
            yaxis=dict(title='Time'),
            width=680,
            height=600
        )

        heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)

        heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Calculate median line
        data_median = np.median(current_dataset.values[:, 2:], axis=0)

        median_trace = go.Scatter(
            y=data_median,
            x=np.linspace(Start_frequency, Stop_frequency, len(data_median)),
            mode='lines',
            hoverinfo='x+y'
        )

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

        # Calculate median line for time
        time_median = np.median(current_dataset.values, axis=1)

        # Plot median line with y-axis labeled with common_time_labels
        time_median_trace = go.Scatter(
            x=time_median,
            y=common_time_labels,
            mode='lines',
            name='Median Line'
        )

        # Layout for the median line graph
        time_median_layout = go.Layout(
            xaxis_title='Intensity [dBm]',
            yaxis_title='Time',
            hovermode='closest',
            showlegend=True,
            width=680,
            height=600
        )

        # Create the median line figure
        time_median_fig = go.Figure(data=[time_median_trace], layout=time_median_layout)

        # Convert the figure to JSON
        time_median_graphJSON = json.dumps(time_median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify({
            'success': True,
            'heatmap_graphJSON': heatmap_graphJSON,
            'median_graphJSON': median_graphJSON,
            'time_median_graphJSON': time_median_graphJSON,
            'hdr_content': hdr_content if hdr_content else 'Hdr File Not Found!!'
        })

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
