from flask import Flask, jsonify, render_template, request
from tkinter.filedialog import asksaveasfile
from tkinter import ttk

app = Flask(__name__)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('save.html')

# Endpoint to handle the save operation
@app.route('/save_file', methods=['POST'])
def save_file():
    # Get filename from frontend
    data = request.get_json()
    filename = data.get('filename')

    # Call save dialog box
    files = [('All Files', '*.*'), ('Python Files', '*.py'), ('Text Document', '*.txt'), ('PNG Files', '*.png'), ('JPEG Files', '*.jpg')]
    file = asksaveasfile(filetypes=files, defaultextension=".txt")

    if file:
        file.write("Your content here")  # You can write your content here if needed
        file.close()
        return jsonify({'message': 'File saved successfully'})
    else:
        return jsonify({'message': 'File not saved'})

if __name__ == '__main__':
    app.run(debug=True)
