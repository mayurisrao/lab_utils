from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10000 * 1024 * 1024  # 10000 MB max upload size (10 GB)
app.config['UPLOAD_FOLDER'] = 'Dataset'

# Global variables
datasets = {}
current_dataset = None
current_y_label = 'Time'  # Default y-axis label

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/chart")
def chart():
    return render_template('chart.html')

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global datasets, current_dataset

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': str(e)})

    try:
        chunk_list = []
        for chunk in pd.read_csv(file_path, chunksize=1000000):
            chunk_list.append(chunk.select_dtypes(include=['number']))
        current_dataset = pd.concat(chunk_list, ignore_index=True)
        datasets[filename] = current_dataset
    except Exception as e:
        return jsonify({'error': 'Failed to load dataset: ' + str(e)})

    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    base_name = os.path.splitext(filename)[0]
    hdr_file_path = None
    for ext in ['_hdr', '.txt']:
        potential_path = os.path.join(downloads_folder, base_name + ext)
        if os.path.isfile(potential_path):
            hdr_file_path = potential_path
            break

    hdr_found = hdr_file_path is not None

    if hdr_found:
        try:
            with open(hdr_file_path, 'r') as f:
                hdr_content = f.read()
            return jsonify({'success': 'Dataset uploaded successfully', 'hdr_content': hdr_content, 'hdr_found': True})
        except Exception as e:
            return jsonify({'success': 'Dataset uploaded, but failed to read HDR file: ' + str(e), 'hdr_found': False})
    else:
        return jsonify({'success': 'Dataset uploaded successfully', 'hdr_content': 'There is no HDR File uploaded.', 'hdr_found': False})

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
    if filename in datasets:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        return jsonify({'error': 'Dataset not found'})

@app.route('/stream_data', methods=['POST'])
def stream_data():
    global current_dataset

    data = request.get_json()

    if current_dataset is None:
        current_dataset = pd.DataFrame(columns=data.keys())

    new_data = pd.DataFrame([data])
    current_dataset = pd.concat([current_dataset, new_data], ignore_index=True)

    return jsonify({'success': True})

@app.route('/visualize', methods=['POST'])
def visualize():
    global current_dataset, current_y_label

    if current_dataset is None or current_dataset.empty:
        return jsonify({'error': 'No data available'})

    try:
        Start_frequency = None
        Stop_frequency = None
        Sweep_points = None
        Sweep_time = None
        Start_time = None
        hdr_content = request.json.get('hdrContent', None)
        hdr_found = request.json.get('hdr_found', False)

        x_label = 'Frequency [GHz]'
        y_label = current_y_label

        if hdr_content:
            lines = hdr_content.split('\n')
            for line in lines:
                if line.startswith("Start frequency:"):
                    Start_frequency = float(line.split(": ")[1].strip()) / 1e9
                elif line.startswith("Stop frequency:"):
                    Stop_frequency = float(line.split(": ")[1].strip()) / 1e9
                elif line.startswith("Sweep points:"):
                    Sweep_points = int(line.split(": ")[1].strip())
                elif line.startswith("Sweep time:"):
                    Sweep_time = float(line.split(": ")[1].strip())
                elif line.startswith("Start time:"):
                    Start_time = line.split(": ")[1].strip()

        if Start_frequency is None or Stop_frequency is None or Sweep_points is None or Sweep_time is None or Start_time is None:
            Start_frequency = 0
            Stop_frequency = 1
            Sweep_points = 1
            Sweep_time = 1
            Start_time = '00,00,00'
            x_label = 'Channel'
            y_label = 'Time Period'

        hr, min, sec = map(int, Start_time.split(','))
        start_seconds = hr * 3600 + min * 60 + sec

        time_labels = []
        for i in range(len(current_dataset)):
            time_seconds = start_seconds + i * Sweep_time
            hours = int((time_seconds // 3600) % 24)
            minutes = int((time_seconds // 60) % 60)
            seconds = int(time_seconds % 60)
            new_time = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
            timestamp = pd.to_datetime(new_time, format='%H:%M:%S').strftime('%H,%M,%S')
            time_labels.append(timestamp)

        time_labels = sorted(list(set(time_labels)))
        common_time_labels = time_labels[:len(current_dataset)]

        f_start = Start_frequency
        f_stop = Stop_frequency
        f_sweep = Sweep_points

        heatmap_trace = go.Heatmap(
            z=current_dataset.values,
            colorscale='Inferno',
            zmin=-90,
            zmax=-60,
            x=np.linspace(f_start, f_stop, f_sweep),
            y=common_time_labels
        )

        heatmap_layout = go.Layout(
            xaxis=dict(title=x_label),
            yaxis=dict(title=y_label),
            width=680,
            height=600
        )

        heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)
        heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)

        data_median = np.median(current_dataset.values[:, 2:], axis=0)

        median_trace = go.Scatter(
            y=data_median,
            x=np.linspace(Start_frequency, Stop_frequency, len(data_median)),
            mode='lines',
            hoverinfo='x+y'
        )

        median_layout = go.Layout(
            xaxis_title=x_label,
            yaxis_title='Median Intensity [dBm]',
            hovermode='closest',
            margin=dict(t=2),
            width=700,
            height=600
        )

        median_fig = go.Figure(data=[median_trace], layout=median_layout)
        median_graphJSON = json.dumps(median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        time_median = np.median(current_dataset.values, axis=1)

        time_median_trace = go.Scatter(
            x=time_median,
            y=common_time_labels,
            mode='lines',
            name='Median Line'
        )

        time_median_layout = go.Layout(
            xaxis_title='Intensity [dBm]',
            yaxis_title=y_label,
            hovermode='closest',
            showlegend=True,
            width=680,
            height=600
        )

        time_median_fig = go.Figure(data=[time_median_trace], layout=time_median_layout)
        time_median_graphJSON = json.dumps(time_median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify({
            'success': True,
            'heatmap_graphJSON': heatmap_graphJSON,
            'median_graphJSON': median_graphJSON,
            'time_median_graphJSON': time_median_graphJSON,
            'hdr_content': hdr_content if hdr_content else 'There is no HDR File uploaded.',
            'y_label': y_label
        })

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/update_y_label', methods=['POST'])
def update_y_label():
    global current_y_label

    new_y_label = request.json.get('y_label')

    if new_y_label:
        current_y_label = new_y_label
        return jsonify({'success': 'Y-axis label updated successfully', 'y_label': current_y_label})
    else:
        return jsonify({'error': 'Failed to update Y-axis label'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
