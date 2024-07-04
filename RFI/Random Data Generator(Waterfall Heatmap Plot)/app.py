from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import time

app = Flask(__name__)

# Initial dataset file
current_dataset = None
fake_data_generator = None

def generate_fake_data(dataset_filename):
    """Generate fake data for demonstration and append to the dataset file."""
    while True:
        # Generate random data
        fake_data = np.random.randint(50, 100, size=(10, 10))
        
        # Append the generated data to the dataset file
        with open(dataset_filename, 'a') as file:
            pd.DataFrame(fake_data).to_csv(file, header=False, index=False)
        
        yield fake_data.tolist()
        time.sleep(1)  # Simulate 1 second delay

@app.route('/')
def index():
    return render_template('realtime.html')

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global current_dataset
    global fake_data_generator
    
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
    
    # Set current dataset to the uploaded file
    current_dataset = filename
    
    # Start the fake data generator with the uploaded file name
    fake_data_generator = generate_fake_data(filename)
    
    # Send success message to frontend
    return jsonify({'success': 'Dataset ' + filename + ' uploaded successfully'})

@app.route('/visualize', methods=['GET'])
def visualize():
    global current_dataset
    global fake_data_generator
    
    # Check if dataset is loaded
    if current_dataset is None:
        return jsonify({'error': 'No dataset loaded'})

    try:
        # Generate the waterfall heatmap
        rfi_data = next(fake_data_generator)  # Get the next generated fake data

        # Create the heatmap trace
        trace = go.Heatmap(z=rfi_data,
                           colorscale='Inferno',
                           zmin=np.min(rfi_data),
                           zmax=np.max(rfi_data),
                           x=[i for i in range(len(rfi_data[0]))],  # Assuming columns represent frequencies
                           y=[i for i in range(len(rfi_data))],  # Each row represents a 2-second interval
                           )

        # Create the layout
        layout = go.Layout(title='Waterfall Heatmap',
                           xaxis=dict(title='Frequency (GHz)'),
                           yaxis=dict(title='Time (seconds)'),
                           )

        # Create the figure
        fig = go.Figure(data=[trace], layout=layout)

        # Convert the figure to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Return the JSON data
        return jsonify({'success': True, 'graphJSON': graphJSON})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
