from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import time

app = Flask(__name__)

# Initial dataset file and real-time data
current_dataset = None
realtime_data = None

def fetch_realtime_data():
    """Fetch real-time data from a hypothetical data source."""
    # Replace this with your mechanism to fetch real-time data
    # For demonstration, here we're just generating random data
    return np.random.randint(50, 100, size=(10, 10))

def calculate_time_median(data):
    """Calculate time median from the given data."""
    return np.median(data, axis=0)

@app.route('/')
def index():
    return render_template('real.html')

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
    filename = file.filename
    file.save(filename)
    
    # Replace the current dataset with the uploaded file
    current_dataset = pd.read_csv(filename)
    
    # Handle non-numeric data: Drop non-numeric columns
    current_dataset = current_dataset.select_dtypes(include=['number'])
    
    # Send success message to frontend
    return jsonify({'success': 'Dataset ' + filename + ' uploaded successfully'})

@app.route('/visualize', methods=['GET'])
def visualize():
    global current_dataset, realtime_data
    
    # Check if dataset is loaded
    if current_dataset is None:
        return jsonify({'error': 'No dataset loaded'})

    try:
        # If realtime flag is set, fetch real-time data
        if request.args.get('realtime') == 'true':
            realtime_data = fetch_realtime_data()
        
        # Use real-time data if available, else use uploaded dataset
        data = realtime_data if realtime_data is not None else current_dataset.to_numpy()

        # Calculate time median
        time_median = calculate_time_median(data)

        # Generate the waterfall heatmap
        # Create the heatmap trace
        heatmap_trace = go.Heatmap(z=data,
                                   colorscale='Inferno',
                                   zmin=np.min(data),
                                   zmax=np.max(data),
                                   x=[i for i in range(len(data[0]))],  # Assuming columns represent frequencies
                                   y=[i for i in range(len(data))],  # Each row represents a 2-second interval
                                   )

        # Create the layout for heatmap
        heatmap_layout = go.Layout(title='Waterfall Heatmap',
                                   xaxis=dict(title='Frequency (GHz)'),
                                   yaxis=dict(title='Time (seconds)'),
                                   )

        # Create the heatmap figure
        heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)

        # Convert the heatmap figure to JSON
        heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Create time median plot
        time_median_trace = go.Scatter(x=time_median, y=np.arange(len(time_median)), mode='lines', name='Median Line')

        # Create layout for time median plot
        time_median_layout = go.Layout(title='Time Median Plot',
                                       xaxis=dict(title='Intensity (dBm)'),
                                       yaxis=dict(title='Time (seconds)'),
                                       hovermode='closest',  # Display values of nearest data point on hover
                                       showlegend=True
                                       )

        # Create time median plot figure
        time_median_fig = go.Figure(data=[time_median_trace], layout=time_median_layout)

        # Convert the time median plot figure to JSON
        time_median_graphJSON = json.dumps(time_median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Return the JSON data
        return jsonify({'success': True, 'heatmapJSON': heatmap_graphJSON, 'timeMedianJSON': time_median_graphJSON})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
