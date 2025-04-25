#!/usr/bin/env python
"""
Create Sample SQLite Database with Property Listings
---------------------------------------------------
This script creates a sample SQLite database with property listings
that can be used to test the db_to_json.py script.
"""

import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data
CITIES = ["София", "Пловдив", "Варна", "Бургас"]

DISTRICTS = {
    "София": ["Драгалевци", "Лозенец", "Витоша", "Младост", "Люлин"],
    "Пловдив": ["Център", "Кършияка", "Тракия", "Смирненски"],
    "Варна": ["Чайка", "Виница", "Бриз", "Владиславово"],
    "Бургас": ["Лазур", "Меден Рудник", "Славейков", "Зорница"]
}

PROPERTY_TYPES = ["Къща", "Апартамент", "Студио", "Мезонет"]

# Data for property generation
SAMPLE_PROPERTIES = [
    # Sofia
    {
        "city": "София",
        "district": "Драгалевци",
        "property_type": "Къща",
        "area": 240,
        "area_unit": "квадратни метра",
        "price": 824545,
        "price_unit": "лева",
        "price_per_sqm": 3435,
        "price_per_sqm_unit": "лева"
    },
    {
        "city": "София",
        "district": "Лозенец",
        "property_type": "Апартамент",
        "area": 90,
        "area_unit": "квадратни метра",
        "price": 270000,
        "price_unit": "лева",
        "price_per_sqm": 3000,
        "price_per_sqm_unit": "лева"
    },
    {
        "city": "София",
        "district": "Витоша",
        "property_type": "Къща",
        "area": 200,
        "area_unit": "квадратни метра",
        "price": 650000,
        "price_unit": "лева",
        "price_per_sqm": 3250,
        "price_per_sqm_unit": "лева"
    },
    {
        "city": "София",
        "district": "Младост",
        "property_type": "Апартамент",
        "area": 85,
        "area_unit": "квадратни метра",
        "price": 195000,
        "price_unit": "лева",
        "price_per_sqm": 2294,
        "price_per_sqm_unit": "лева"
    },
    # Plovdiv
    {
        "city": "Пловдив",
        "district": "Център",
        "property_type": "Апартамент",
        "area": 120,
        "area_unit": "квадратни метра",
        "price": 300000,
        "price_unit": "лева",
        "price_per_sqm": 2500,
        "price_per_sqm_unit": "лева"
    },
    {
        "city": "Пловдив",
        "district": "Кършияка",
        "property_type": "Къща",
        "area": 180,
        "area_unit": "квадратни метра",
        "price": 450000,
        "price_unit": "лева",
        "price_per_sqm": 2500,
        "price_per_sqm_unit": "лева"
    },
    # Varna
    {
        "city": "Варна",
        "district": "Чайка",
        "property_type": "Апартамент",
        "area": 95,
        "area_unit": "квадратни метра",
        "price": 200000,
        "price_unit": "лева",
        "price_per_sqm": 2105,
        "price_per_sqm_unit": "лева"
    },
    {
        "city": "Варна",
        "district": "Виница",
        "property_type": "Къща",
        "area": 150,
        "area_unit": "квадратни метра",
        "price": 360000,
        "price_unit": "лева",
        "price_per_sqm": 2400,
        "price_per_sqm_unit": "лева"
    },
    # Burgas
    {
        "city": "Бургас",
        "district": "Лазур",
        "property_type": "Апартамент",
        "area": 85,
        "area_unit": "квадратни метра",
        "price": 220000,
        "price_unit": "лева",
        "price_per_sqm": 2588,
        "price_per_sqm_unit": "лева"
    },
    {
        "city": "Бургас",
        "district": "Меден Рудник",
        "property_type": "Къща",
        "area": 200,
        "area_unit": "квадратни метра",
        "price": 380000,
        "price_unit": "лева",
        "price_per_sqm": 1900,
        "price_per_sqm_unit": "лева"
    }
]

def create_database(database_file):
    """Create a new SQLite database with property listings"""
    
    # Remove existing database file if it exists
    if os.path.exists(database_file):
        os.remove(database_file)
        logger.info(f"Removed existing database: {database_file}")
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        district TEXT NOT NULL,
        property_type TEXT NOT NULL,
        area REAL NOT NULL,
        area_unit TEXT NOT NULL,
        price REAL NOT NULL,
        price_unit TEXT NOT NULL,
        price_per_sqm REAL NOT NULL,
        price_per_sqm_unit TEXT NOT NULL
    )
    ''')
    
    # Insert sample data
    for property_data in SAMPLE_PROPERTIES:
        cursor.execute('''
        INSERT INTO properties (
            city, district, property_type, area, area_unit, 
            price, price_unit, price_per_sqm, price_per_sqm_unit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            property_data["city"],
            property_data["district"],
            property_data["property_type"],
            property_data["area"],
            property_data["area_unit"],
            property_data["price"],
            property_data["price_unit"],
            property_data["price_per_sqm"],
            property_data["price_per_sqm_unit"]
        ))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    logger.info(f"Database created successfully: {database_file}")
    logger.info(f"Added {len(SAMPLE_PROPERTIES)} property listings")

def main():
    """Main function to create the sample database"""
    
    database_file = "properties.db"
    
    try:
        create_database(database_file)
        return 0
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 