"""
Web server for VeloCompare functionality
"""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import tempfile
from velo_compare import VeloCompare

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}  # Added CSV support

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main comparison page."""
    return send_from_directory('.', 'velo_compare.html')

@app.route('/compare', methods=['POST'])
def compare_sheets():
    """Handle file uploads and comparison."""
    if 'file_a' not in request.files or 'file_b' not in request.files:
        return jsonify({'error': 'Both files are required'}), 400
    
    file_a = request.files['file_a']
    file_b = request.files['file_b']
    
    if file_a.filename == '' or file_b.filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    if not (allowed_file(file_a.filename) and allowed_file(file_b.filename)):
        return jsonify({'error': 'Invalid file type. Please upload .xlsx, .xls, or .csv files'}), 400
    
    try:
        # Save uploaded files
        filename_a = secure_filename(file_a.filename)
        filename_b = secure_filename(file_b.filename)
        
        filepath_a = os.path.join(app.config['UPLOAD_FOLDER'], filename_a)
        filepath_b = os.path.join(app.config['UPLOAD_FOLDER'], filename_b)
        
        file_a.save(filepath_a)
        file_b.save(filepath_b)
        
        # Get key columns if provided
        key_columns = None
        if 'key_columns' in request.form and request.form['key_columns'].strip():
            key_columns = [col.strip() for col in request.form['key_columns'].split(',')]
        
        # Create output directory
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'velo_compare_results')
        os.makedirs(output_dir, exist_ok=True)
        
        # Run comparison
        comparator = VeloCompare()
        if not comparator.load_sheets(filepath_a, filepath_b):
            return jsonify({'error': 'Failed to load sheets'}), 500
        
        results = comparator.compare_sheets(key_columns)
        if not results:
            return jsonify({'error': 'Comparison failed'}), 500
        
        # Export results
        if not comparator.export_results(output_dir):
            return jsonify({'error': 'Failed to export results'}), 500
        
        # Clean up uploaded files
        os.remove(filepath_a)
        os.remove(filepath_b)
        
        return jsonify({
            'total_rows_a': results['total_rows_a'],
            'total_rows_b': results['total_rows_b'],
            'unique_to_a': results['unique_to_a'],
            'unique_to_b': results['unique_to_b'],
            'key_columns_used': results['key_columns_used']
        })
        
    except Exception as e:
        # Clean up files in case of error
        if os.path.exists(filepath_a):
            os.remove(filepath_a)
        if os.path.exists(filepath_b):
            os.remove(filepath_b)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download comparison result files."""
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'velo_compare_results')
    return send_from_directory(output_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 