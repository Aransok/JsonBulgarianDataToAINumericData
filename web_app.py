#!/usr/bin/env python
"""
Property Listings Web Application
--------------------------------
A simple web interface for the PDF generation pipeline.
Allows users to:
- Select a database type
- Configure database connection
- Generate JSON and PDF files
- Download the results
"""

import os
import json
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename

# Import application modules
import db_to_json
import main as pdf_generator

# Create Flask application
app = Flask(__name__)
app.secret_key = 'property_listings_secret_key'

# Create upload and output directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Database configurations
SUPPORTED_DB_TYPES = {
    'sqlite': 'SQLite',
    'postgresql': 'PostgreSQL',
    'mysql': 'MySQL', 
    'sqlserver': 'SQL Server',
    'mongodb': 'MongoDB'
}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', db_types=SUPPORTED_DB_TYPES)

@app.route('/config/<db_type>', methods=['GET'])
def db_config(db_type):
    """Render the database configuration form for the selected database type"""
    if db_type not in SUPPORTED_DB_TYPES:
        flash('Unsupported database type', 'error')
        return redirect(url_for('index'))
    
    return render_template('db_config.html', db_type=db_type, db_name=SUPPORTED_DB_TYPES[db_type])

@app.route('/generate', methods=['POST'])
def generate():
    """Process the form submission and generate the output files"""
    db_type = request.form.get('db_type')
    
    # Validate database type
    if db_type not in SUPPORTED_DB_TYPES:
        flash('Unsupported database type', 'error')
        return redirect(url_for('index'))
    
    try:
        # Create a unique session ID
        session_id = str(uuid.uuid4())
        
        # Create output directory for this session
        session_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Paths for output files
        json_file = os.path.join(session_dir, 'input.json')
        pdf_file = os.path.join(session_dir, 'property_listings_en.pdf')
        config_file = os.path.join(session_dir, 'db_config.json')
        
        # Create database config
        db_config = create_db_config(db_type, request.form, request.files)
        
        # Save database config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(db_config, f, ensure_ascii=False, indent=2)
        
        # Convert database to JSON
        connector = db_to_json.create_connector(db_config['type'], db_config['connection'])
        data = db_to_json.fetch_and_format_data(connector)
        
        # Save JSON data
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Generate PDF
        translated_data = pdf_generator.translate_data(data)
        pdf_generator.generate_pdf(translated_data, pdf_file)
        
        return render_template('result.html', 
                              session_id=session_id,
                              json_file='input.json',
                              pdf_file='property_listings_en.pdf')
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('db_config', db_type=db_type))

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    """Download a generated file"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], session_id, secure_filename(filename))
    
    if not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    # Determine the download file name
    if filename.endswith('.json'):
        download_name = 'property_data.json'
    elif filename.endswith('.pdf'):
        download_name = 'property_listings.pdf'
    else:
        download_name = filename
    
    return send_file(file_path, as_attachment=True, download_name=download_name)

def create_db_config(db_type, form_data, files) -> Dict[str, Any]:
    """Create a database configuration dictionary from form data"""
    config = {
        "type": db_type,
        "connection": {}
    }
    
    if db_type == 'sqlite':
        # Handle SQLite file upload
        if 'sqlite_file' in files and files['sqlite_file'].filename:
            file = files['sqlite_file']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            config['connection']['database_file'] = file_path
        else:
            # Use the provided path
            config['connection']['database_file'] = form_data.get('sqlite_path', 'properties.db')
    
    elif db_type == 'mongodb':
        config['connection']['connection_string'] = form_data.get('mongodb_uri', 'mongodb://localhost:27017')
        config['connection']['database'] = form_data.get('mongodb_db', 'properties')
        config['connection']['collection'] = form_data.get('mongodb_collection', 'listings')
    
    else:  # PostgreSQL, MySQL, SQL Server
        config['connection']['host'] = form_data.get('host', 'localhost')
        
        # Add port if provided
        if form_data.get('port'):
            try:
                config['connection']['port'] = int(form_data.get('port'))
            except ValueError:
                pass
        
        # Add database name
        if form_data.get('database'):
            config['connection']['database'] = form_data.get('database')
        
        # Add authentication if provided
        if form_data.get('username'):
            config['connection']['user'] = form_data.get('username')
        
        if form_data.get('password'):
            config['connection']['password'] = form_data.get('password')
    
    return config

# Create HTML templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Create index.html template
INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Property Listings Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 2rem; }
        .db-card { transition: transform 0.3s; cursor: pointer; }
        .db-card:hover { transform: translateY(-5px); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row mb-4">
            <div class="col">
                <h1 class="display-4 text-center">Property Listings Generator</h1>
                <p class="lead text-center">Generate property listings PDF from database sources</p>
            </div>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category if category != 'error' else 'danger' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="card shadow">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Select Database Type</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            {% for db_id, db_name in db_types.items() %}
                                <div class="col-md-4 mb-3">
                                    <div class="card db-card shadow-sm h-100" onclick="window.location='{{ url_for('db_config', db_type=db_id) }}'">
                                        <div class="card-body text-center">
                                            <h3>{{ db_name }}</h3>
                                            <p class="text-muted">Configure and connect to {{ db_name }}</p>
                                        </div>
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Create db_config.html template
DB_CONFIG_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ db_name }} Configuration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 2rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row mb-4">
            <div class="col">
                <h1 class="display-4 text-center">{{ db_name }} Configuration</h1>
                <p class="lead text-center">Configure your {{ db_name }} connection</p>
            </div>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category if category != 'error' else 'danger' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <div class="card shadow">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Connection Settings</h5>
                    </div>
                    <div class="card-body">
                        <form method="post" action="{{ url_for('generate') }}" enctype="multipart/form-data">
                            <input type="hidden" name="db_type" value="{{ db_type }}">
                            
                            {% if db_type == 'sqlite' %}
                                <div class="mb-3">
                                    <label class="form-label">Upload SQLite Database File:</label>
                                    <input type="file" name="sqlite_file" class="form-control">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Or Specify Path:</label>
                                    <input type="text" name="sqlite_path" class="form-control" value="properties.db">
                                    <div class="form-text">If no file is uploaded, this path will be used</div>
                                </div>
                            {% elif db_type == 'mongodb' %}
                                <div class="mb-3">
                                    <label class="form-label">MongoDB URI:</label>
                                    <input type="text" name="mongodb_uri" class="form-control" value="mongodb://localhost:27017">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Database Name:</label>
                                    <input type="text" name="mongodb_db" class="form-control" value="properties">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Collection Name:</label>
                                    <input type="text" name="mongodb_collection" class="form-control" value="listings">
                                </div>
                            {% else %}
                                <div class="mb-3">
                                    <label class="form-label">Host:</label>
                                    <input type="text" name="host" class="form-control" value="localhost">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Port:</label>
                                    <input type="text" name="port" class="form-control" 
                                           value="{% if db_type == 'postgresql' %}5432{% elif db_type == 'mysql' %}3306{% elif db_type == 'sqlserver' %}1433{% endif %}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Database Name:</label>
                                    <input type="text" name="database" class="form-control" value="properties">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Username:</label>
                                    <input type="text" name="username" class="form-control">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password:</label>
                                    <input type="password" name="password" class="form-control">
                                </div>
                            {% endif %}
                            
                            <div class="mb-3">
                                <a href="{{ url_for('index') }}" class="btn btn-secondary">Back</a>
                                <button type="submit" class="btn btn-primary">Generate PDF</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Create result.html template
RESULT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Generation Results</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 2rem; }
        .download-card { transition: transform 0.3s; }
        .download-card:hover { transform: translateY(-5px); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row mb-4">
            <div class="col">
                <h1 class="display-4 text-center">Generation Completed!</h1>
                <p class="lead text-center">Your property listings have been successfully generated</p>
            </div>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category if category != 'error' else 'danger' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card download-card shadow h-100">
                    <div class="card-body text-center">
                        <h3>JSON Data</h3>
                        <p>Download the raw property data in JSON format.</p>
                        <a href="{{ url_for('download_file', session_id=session_id, filename=json_file) }}" class="btn btn-primary">
                            Download JSON
                        </a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card download-card shadow h-100">
                    <div class="card-body text-center">
                        <h3>PDF Report</h3>
                        <p>Download the translated property listings PDF.</p>
                        <a href="{{ url_for('download_file', session_id=session_id, filename=pdf_file) }}" class="btn btn-success">
                            Download PDF
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col text-center mt-3">
                <a href="{{ url_for('index') }}" class="btn btn-secondary">Start Over</a>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Save the templates
def save_templates():
    """Save HTML templates to the templates directory"""
    with open(os.path.join(TEMPLATES_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(INDEX_HTML)
    
    with open(os.path.join(TEMPLATES_DIR, 'db_config.html'), 'w', encoding='utf-8') as f:
        f.write(DB_CONFIG_HTML)
    
    with open(os.path.join(TEMPLATES_DIR, 'result.html'), 'w', encoding='utf-8') as f:
        f.write(RESULT_HTML)

# Save templates when the module is imported
save_templates()

if __name__ == '__main__':
    # Create templates if they don't exist
    save_templates()
    
    # Run the Flask application
    app.run(debug=True) 