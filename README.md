# Real Estate Listings Translator & Formatter

This Python project processes property listings from a JSON file, translates Bulgarian text to English, and formats the data into a clean PDF report. It supports getting data from various database systems.

## Features

- Translates all Bulgarian text into English
- Converts numeric values into their Bulgarian word equivalents using English letters
- Generates a well-structured PDF report with a clean layout
- **Handles various JSON structures** - the program is designed to work with different data formats
- **Database Integration** - supports retrieving data from PostgreSQL, MySQL, SQLite, and SQL Server

## Requirements

- Python 3.10 or higher
- Required Python packages:
  - deep-translator
  - fpdf
  - Database drivers (as needed):
    - psycopg2-binary (for PostgreSQL)
    - mysql-connector-python (for MySQL)
    - pyodbc (for SQL Server)

## Setup Instructions

1. Clone this repository or download the project files

2. Install the required dependencies:

   ```bash
   pip install deep-translator fpdf
   ```

   Or use the requirements.txt file:

   ```bash
   pip install -r requirements.txt
   ```

   For database support, install the appropriate driver:

   ```bash
   # For PostgreSQL
   pip install psycopg2-binary

   # For MySQL
   pip install mysql-connector-python

   # For SQL Server
   pip install pyodbc
   ```

3. Create your own `input.json` file in the project directory (you can use `sample_input.json` as a template)

   **Important**: The actual input data should not be committed to the repository for privacy reasons. The `.gitignore` file is set up to exclude all JSON and PDF files except for the sample file.

4. Run the main script:

   ```bash
   python main.py [input_file.json] [output_file.pdf]
   ```

   If no arguments are provided, the program will use `input.json` as the input file and
   `property_listings_en.pdf` as the output file.

5. Check the output PDF file in the same directory

## Database Integration

The project includes a database connector script (`db_to_json.py`) that can retrieve property listings from various database types and format them for use with the main program:

### Setting Up the Database

1. For testing purposes, you can create a sample SQLite database:

   ```bash
   python create_sample_db.py
   ```

   This will create a `properties.db` file with sample property listings.

2. Configure your database connection by editing `db_config.json`:

   ```json
   {
     "type": "sqlite",
     "connection": {
       "database_file": "properties.db"
     }
   }
   ```

   The configuration supports different database types:

   - **SQLite**:

     ```json
     {
       "type": "sqlite",
       "connection": {
         "database_file": "path/to/your/database.db"
       }
     }
     ```

   - **PostgreSQL**:

     ```json
     {
       "type": "postgresql",
       "connection": {
         "host": "localhost",
         "port": 5432,
         "database": "your_database",
         "user": "your_username",
         "password": "your_password"
       }
     }
     ```

   - **MySQL**:

     ```json
     {
       "type": "mysql",
       "connection": {
         "host": "localhost",
         "port": 3306,
         "database": "your_database",
         "user": "your_username",
         "password": "your_password"
       }
     }
     ```

   - **SQL Server**:
     ```json
     {
       "type": "sqlserver",
       "connection": {
         "server": "your_server",
         "database": "your_database",
         "user": "your_username",
         "password": "your_password"
       }
     }
     ```

3. Retrieve data from the database and save it as JSON:

   ```bash
   python db_to_json.py --config db_config.json --output input.json
   ```

   This will extract property listings from the database and save them in the format required by the main application.

### Database Schema

The database connector expects a table named `properties` with the following columns:

- `city` - City name (e.g., "София")
- `district` - District name (e.g., "Драгалевци")
- `property_type` - Property type (e.g., "Къща", "Апартамент")
- `area` - Area value (e.g., 240)
- `area_unit` - Area unit (e.g., "квадратни метра")
- `price` - Price value (e.g., 824545)
- `price_unit` - Price unit (e.g., "лева")
- `price_per_sqm` - Price per square meter value (e.g., 3435)
- `price_per_sqm_unit` - Price per square meter unit (e.g., "лева")

## Input Format Flexibility

The program is designed to handle various JSON structures. It automatically detects and processes property data regardless of the JSON format. Here are some examples of supported formats:

### City-Based Structure

```json
{
  "София": [
    {
      "квартал": "Драгалевци",
      "тип": "Къща",
      "площ": "240 квадратни метра",
      "цена": "824545 лева"
    }
  ],
  "Пловдив": [
    {
      "квартал": "Център",
      "тип": "Апартамент",
      "площ": "120 квадратни метра",
      "цена": "300000 лева"
    }
  ]
}
```

### Nested Structure

```json
{
  "data": {
    "properties": [
      {
        "град": "София",
        "квартал": "Младост",
        "тип": "Апартамент",
        "площ": "85 квадратни метра",
        "цена": "185000 лева"
      }
    ]
  }
}
```

## Creating Your Own Input File

To create your own `input.json`:

1. Use one of the JSON structures shown above as a template
2. Add your own property listings with the following fields (in Bulgarian):
   - City/град (e.g., "София", "Пловдив", "Варна")
   - District/квартал
   - Type/тип (e.g., "Къща", "Апартамент")
   - Area/площ (e.g., "240 квадратни метра")
   - Price/цена (e.g., "824545 лева")
3. Save the file as `input.json` in the project directory

The input file will not be committed to the repository (it's included in `.gitignore`).

## Output Format

The output PDF will display:

- City names as headers
- District information (bold)
- Property details with bullet points
- **Numeric values are presented in Bulgarian words (using English letters)** rather than showing the original numbers
  - Example: "Price: osemstotin dvadeset i chetiri hilyadi petstotin chetirideset i pet leva"

## Version Control Notes

The `.gitignore` file is configured to exclude:

- All `.json` files (to protect your data)
- All `.pdf` files (generated outputs)
- Python bytecode and virtual environment folders
- Database files (\*.db)

Only the code files and documentation are meant to be committed to the repository.

## Troubleshooting

If you encounter any issues with the translation API, the program will still run and output the original text.

## Files Included

- `main.py` - The main script for translating and generating PDFs
- `db_to_json.py` - Script for retrieving data from databases
- `create_sample_db.py` - Script to create a sample SQLite database
- `README.md` - This documentation file
- `requirements.txt` - Dependencies list
- `Bulgarian_Number_Reference.md` - Reference guide for Bulgarian number words
- `sample_input.json` - Sample input file with dummy data
- `db_config.json` - Sample database configuration
- `.gitignore` - Configuration to exclude input/output files from version control
