# Property Listings Generator

A comprehensive tool for generating property listings PDFs from various database sources.

## Features

- Extract property data from multiple database types:
  - SQLite
  - PostgreSQL
  - MySQL
  - SQL Server
  - MongoDB (New!)
- Convert property data to structured JSON format
- Translate Bulgarian property data to English
- Generate professionally formatted PDF reports
- Command-line interface for automation
- Web interface for easy access

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Aransok/JsonBulgarianDataToAINumericData.git
   cd JsonBulgarianDataToAINumericData
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Install database drivers:

   Uncomment the appropriate lines in `requirements.txt` based on your needs:

   ```bash
   # For PostgreSQL
   pip install psycopg2-binary>=2.9.9

   # For MySQL
   pip install mysql-connector-python>=8.2.0

   # For SQL Server
   pip install pyodbc>=4.0.39

   # For MongoDB (already enabled by default)
   pip install pymongo>=4.6.2
   ```

## Usage

### Basic Process

The property listings generator follows a three-step process:

1. Create or connect to a database with property data
2. Extract and convert database data to JSON format
3. Generate a translated PDF from the JSON data

### Command Line Interface

The new CLI provides a user-friendly way to interact with the application:

```bash
# Create a sample SQLite database
python property_cli.py create-db --output properties.db

# Convert database to JSON
python property_cli.py db-to-json --config db_config.json --output input.json

# Generate PDF from JSON
python property_cli.py generate-pdf --input input.json --output property_listings_en.pdf

# Run the full process
python property_cli.py full-process --db-type sqlite --db-file properties.db --output properties.pdf

# List supported database types
python property_cli.py list-db-types
```

### Web Interface

The new web interface provides a graphical way to interact with the application:

```bash
# Start the web server
python web_app.py
```

Then open your browser and navigate to http://localhost:5000

The web interface allows you to:

1. Select a database type
2. Configure the database connection
3. Generate and download JSON and PDF files

### Database Configuration

#### SQLite

```json
{
  "type": "sqlite",
  "connection": {
    "database_file": "properties.db"
  }
}
```

#### PostgreSQL

```json
{
  "type": "postgresql",
  "connection": {
    "host": "localhost",
    "port": 5432,
    "database": "properties",
    "user": "username",
    "password": "password"
  }
}
```

#### MySQL

```json
{
  "type": "mysql",
  "connection": {
    "host": "localhost",
    "port": 3306,
    "database": "properties",
    "user": "username",
    "password": "password"
  }
}
```

#### SQL Server

```json
{
  "type": "sqlserver",
  "connection": {
    "server": "localhost",
    "database": "properties",
    "user": "username",
    "password": "password"
  }
}
```

#### MongoDB (New!)

```json
{
  "type": "mongodb",
  "connection": {
    "connection_string": "mongodb://localhost:27017",
    "database": "properties",
    "collection": "listings"
  }
}
```

## Direct Script Usage

If you prefer to use the individual scripts directly:

### Create a Sample Database

```bash
python create_sample_db.py
```

### Convert Database to JSON

```bash
python db_to_json.py --config db_config.json --output input.json
```

### Generate PDF from JSON

```bash
python main.py input.json property_listings_en.pdf
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
