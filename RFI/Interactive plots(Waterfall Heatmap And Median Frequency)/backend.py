from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)

# Initial dataset file
current_dataset = None

@app.route('/')
def index():
    return render_template('load_dataset.html')

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
    global current_dataset
    
    # Check if dataset is loaded
    if current_dataset is None:
        return jsonify({'error': 'No dataset loaded'})

    try:
        # Generate the waterfall heatmap
        rfi_data = np.array(current_dataset)

        # Create the heatmap trace
        heatmap_trace = go.Heatmap(z=rfi_data,
                                   colorscale='Inferno',
                                   zmin=-90,
                                   zmax=-60,
                                   x=[i for i in range(rfi_data.shape[1])],  # Assuming columns represent frequencies
                                   y=[i * 2 for i in range(rfi_data.shape[0])],  # Each row represents a 2-second interval
                                   )

        # Create the layout for heatmap
        heatmap_layout = go.Layout(
                                   xaxis=dict(title='Frequency (GHz)'),
                                   yaxis=dict(title='Time (seconds)'),
                                   width=900,  # Adjust width as desired
                                   height=600  # Adjust height as desired
                                   )

        # Create the heatmap figure
        heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)

        # Convert the heatmap figure to JSON
        heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Calculate median
        data_median = np.median(rfi_data[:, 2:], axis=0)

        # Create Plotly figure for median plot with adjusted margin
        median_trace = go.Scatter(y=data_median, x=np.linspace(0.5, 4.0, len(data_median)), mode='lines', hoverinfo='x+y')

        # Create layout for median plot with adjusted margin and increased width and height
        median_layout = go.Layout(
                                  xaxis_title='Frequency(GHz)',
                                  yaxis_title='Median Intensity (dBm)',
                                  xaxis=dict(autorange="reversed", type="linear"),
                                  yaxis=dict(autorange="reversed", type="linear"),
                                  hovermode='closest',
                                  margin=dict(t=2),  # Adjust the top margin to position the chart 20 units above
                                  width=950,  # Adjust width as desired
                                  height=400  # Adjust height as desired
                                  )

        # Create the median plot figure
        median_fig = go.Figure(data=[median_trace], layout=median_layout)

        # Convert the median plot figure to JSON
        median_graphJSON = json.dumps(median_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Return the JSON data for both charts
        return jsonify({'success': True, 'heatmap_graphJSON': heatmap_graphJSON, 'median_graphJSON': median_graphJSON})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
