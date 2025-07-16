#!/usr/bin/env python3
"""
VeloVerify Web - Simplified web-based version
A basic web interface for CSV processing without heavy dependencies
"""

import os
import csv
import json
from datetime import datetime
from io import StringIO

# Try to use minimal dependencies
try:
    from flask import Flask, render_template_string, request, jsonify, send_file
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# Simple HTTP server fallback
import http.server
import socketserver
import webbrowser
import threading
import time

class SimpleCSVProcessor:
    """Basic CSV processor without pandas dependency."""
    
    def __init__(self):
        self.results = {}
    
    def process_csv_content(self, csv_content):
        """Process CSV content and return basic statistics."""
        try:
            # Parse CSV
            csv_reader = csv.DictReader(StringIO(csv_content))
            rows = list(csv_reader)
            
            if not rows:
                return {"error": "No data found in CSV"}
            
            # Basic processing
            total_rows = len(rows)
            columns = list(rows[0].keys()) if rows else []
            
            # Look for pole-related data
            pole_columns = [col for col in columns if 'pole' in col.lower()]
            date_columns = [col for col in columns if any(word in col.lower() for word in ['date', 'time', 'modified'])]
            
            # Basic statistics
            stats = {
                "total_rows": total_rows,
                "total_columns": len(columns),
                "columns": columns[:10],  # First 10 columns
                "pole_columns": pole_columns,
                "date_columns": date_columns,
                "sample_data": rows[:5] if len(rows) > 5 else rows,  # First 5 rows
                "processing_time": datetime.now().isoformat(),
                "status": "success"
            }
            
            # Look for pole permission entries
            pole_permission_count = 0
            for row in rows:
                for value in row.values():
                    if value and 'pole permission' in str(value).lower():
                        pole_permission_count += 1
                        break
            
            stats["pole_permission_entries"] = pole_permission_count
            
            return stats
            
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VeloVerify Web - CSV Processor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #366092;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .upload-area {
            border: 3px dashed #366092;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            background: #f8f9fa;
            transition: background-color 0.3s ease;
        }
        .upload-area:hover {
            background: #e9ecef;
        }
        .upload-area.dragover {
            background: #d1ecf1;
            border-color: #17a2b8;
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            background: #366092;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .upload-btn:hover {
            background: #285a7a;
        }
        .results {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #366092;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #366092;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .columns-list {
            max-height: 200px;
            overflow-y: auto;
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .sample-data {
            max-height: 300px;
            overflow: auto;
            background: white;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 VeloVerify Web</h1>
        <p class="subtitle">Simplified CSV Processor for Pole Permissions Data</p>
        
        <div class="upload-area" id="uploadArea">
            <h3>📁 Upload CSV File</h3>
            <p>Drag and drop your CSV file here, or click to browse</p>
            <input type="file" id="fileInput" class="file-input" accept=".csv" />
            <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                Choose CSV File
            </button>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            <div class="spinner"></div>
            <p>Processing CSV file...</p>
        </div>
        
        <div id="results" class="results">
            <h3>📊 Processing Results</h3>
            <div id="statsGrid" class="stat-grid"></div>
            <div id="detailsSection"></div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const results = document.getElementById('results');
        const loading = document.getElementById('loading');
        const statsGrid = document.getElementById('statsGrid');
        const detailsSection = document.getElementById('detailsSection');

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.toLowerCase().endsWith('.csv')) {
                showError('Please select a CSV file.');
                return;
            }

            showLoading();
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const csvContent = e.target.result;
                processCSV(csvContent);
            };
            reader.readAsText(file);
        }

        function showLoading() {
            loading.style.display = 'block';
            results.classList.remove('show');
        }

        function hideLoading() {
            loading.style.display = 'none';
        }

        function showError(message) {
            hideLoading();
            detailsSection.innerHTML = `<div class="error">${message}</div>`;
            results.classList.add('show');
        }

        function showSuccess(message) {
            detailsSection.innerHTML = `<div class="success">${message}</div>` + detailsSection.innerHTML;
        }

        function processCSV(csvContent) {
            fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({csv_content: csvContent})
            })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data);
                }
            })
            .catch(error => {
                hideLoading();
                showError('Error processing file: ' + error.message);
            });
        }

        function displayResults(data) {
            // Display statistics
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${data.total_rows}</div>
                    <div class="stat-label">Total Rows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${data.total_columns}</div>
                    <div class="stat-label">Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${data.pole_permission_entries}</div>
                    <div class="stat-label">Pole Permissions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${data.pole_columns.length}</div>
                    <div class="stat-label">Pole Columns</div>
                </div>
            `;

            // Display details
            let detailsHTML = '';
            
            if (data.columns.length > 0) {
                detailsHTML += `
                    <h4>📋 Columns Found (first 10):</h4>
                    <div class="columns-list">
                        ${data.columns.map(col => `<span style="display: inline-block; margin: 3px; padding: 5px 10px; background: #e9ecef; border-radius: 3px; font-size: 12px;">${col}</span>`).join('')}
                    </div>
                `;
            }

            if (data.pole_columns.length > 0) {
                detailsHTML += `
                    <h4>🏗️ Pole-Related Columns:</h4>
                    <div class="columns-list">
                        ${data.pole_columns.map(col => `<span style="display: inline-block; margin: 3px; padding: 5px 10px; background: #d1ecf1; border-radius: 3px; font-size: 12px;">${col}</span>`).join('')}
                    </div>
                `;
            }

            if (data.sample_data.length > 0) {
                detailsHTML += `
                    <h4>📄 Sample Data (first 5 rows):</h4>
                    <div class="sample-data">
                        <pre>${JSON.stringify(data.sample_data, null, 2)}</pre>
                    </div>
                `;
            }

            detailsSection.innerHTML = detailsHTML;
            showSuccess(`✅ Successfully processed CSV file! Found ${data.pole_permission_entries} pole permission entries.`);
            results.classList.add('show');
        }
    </script>
</body>
</html>
"""

def create_flask_app():
    """Create Flask web application."""
    app = Flask(__name__)
    processor = SimpleCSVProcessor()
    
    @app.route('/')
    def index():
        return HTML_TEMPLATE
    
    @app.route('/process', methods=['POST'])
    def process_csv():
        try:
            data = request.get_json()
            csv_content = data.get('csv_content', '')
            
            if not csv_content:
                return jsonify({"error": "No CSV content provided"})
            
            results = processor.process_csv_content(csv_content)
            return jsonify(results)
            
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"})
    
    return app

def run_web_server():
    """Run the web server."""
    if HAS_FLASK:
        print("🚀 Starting VeloVerify Web Server with Flask...")
        app = create_flask_app()
        
        # Start server in a separate thread
        def start_server():
            app.run(host='127.0.0.1', port=5000, debug=False)
        
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        webbrowser.open('http://127.0.0.1:5000')
        
        print("✅ VeloVerify Web is running!")
        print("🌐 URL: http://127.0.0.1:5000")
        print("📝 Access the application in your web browser")
        print("⏹️  Press Ctrl+C to stop the server")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")
            
    else:
        print("❌ Flask not available. Please install Flask:")
        print("   pip install flask")
        print("\nAlternatively, you can run a simple HTTP server:")
        print("   python -m http.server 8000")

if __name__ == "__main__":
    run_web_server() 