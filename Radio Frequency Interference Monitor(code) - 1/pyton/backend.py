from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import os
import json
import plotly.graph_objs as go

app = Flask(__name__)

# Initial dataset
current_dataset = None

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global current_dataset
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save uploaded file
    filename = file.filename
    folder_name = "Dataset"  # Folder to save the dataset
    file.save(os.path.join(folder_name, filename))

    # Read dataset
    current_dataset = pd.read_csv(os.path.join(folder_name, filename))
    current_dataset = current_dataset.select_dtypes(include=['number'])
    
    return jsonify({'success': 'Dataset uploaded successfully'})

@app.route('/visualize', methods=['GET'])
def visualize():
    global current_dataset
    if current_dataset is None or current_dataset.empty:
        return jsonify({'error': 'No data available'})

    try:
        # Sample visualization code (replace with your actual visualization code)
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        fig = go.Figure(data=go.Scatter(x=x, y=y))
        plot_data = json.dumps(fig, cls=go.io.to_json.PlotlyJSONEncoder)
        
        return jsonify({'success': True, 'plot_data': plot_data})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
