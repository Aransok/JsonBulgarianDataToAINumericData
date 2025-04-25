#!/usr/bin/env python
"""
Database to JSON converter for Real Estate Listings
---------------------------------------------------
This script connects to various database types, retrieves property listings,
and formats them into the JSON structure required by the main application.

Supported databases:
- PostgreSQL
- MySQL
- SQLite
- SQL Server
"""

import json
import os
import argparse
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DBConnector(ABC):
    """Abstract base class for database connectors"""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database"""
        pass
    
    @abstractmethod
    def get_cities(self) -> List[str]:
        """Get list of all cities with property listings"""
        pass
    
    @abstractmethod
    def get_properties_by_city(self, city: str) -> List[Dict[str, Any]]:
        """Get all property listings for a specific city"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the database connection"""
        pass

class PostgreSQLConnector(DBConnector):
    """PostgreSQL database connector"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to PostgreSQL database")
        except ImportError:
            logger.error("psycopg2 module not found. Please install it using: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise
    
    def get_cities(self) -> List[str]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT DISTINCT city
            FROM properties
            ORDER BY city
            """
            self.cursor.execute(query)
            cities = [row[0] for row in self.cursor.fetchall()]
            return cities
        except Exception as e:
            logger.error(f"Error retrieving cities: {e}")
            return []
    
    def get_properties_by_city(self, city: str) -> List[Dict[str, Any]]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT district, property_type, area, area_unit, price, price_unit, price_per_sqm, price_per_sqm_unit
            FROM properties
            WHERE city = %s
            """
            self.cursor.execute(query, (city,))
            
            properties = []
            for row in self.cursor.fetchall():
                # Format numbers to remove .0 decimal points
                area = int(row[2]) if row[2] == int(row[2]) else row[2]
                price = int(row[4]) if row[4] == int(row[4]) else row[4]
                price_per_sqm = int(row[6]) if row[6] == int(row[6]) else row[6]
                
                property_data = {
                    "квартал": row[0],
                    "тип": row[1],
                    "площ": f"{area} {row[3]}",
                    "цена": f"{price} {row[5]}",
                    "цена на квадратен метър": f"{price_per_sqm} {row[7]}"
                }
                properties.append(property_data)
            
            return properties
        except Exception as e:
            logger.error(f"Error retrieving properties for city {city}: {e}")
            return []
    
    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed")

class MySQLConnector(DBConnector):
    """MySQL database connector"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to MySQL database")
        except ImportError:
            logger.error("mysql-connector-python module not found. Please install it using: pip install mysql-connector-python")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to MySQL database: {e}")
            raise
    
    def get_cities(self) -> List[str]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT DISTINCT city
            FROM properties
            ORDER BY city
            """
            self.cursor.execute(query)
            cities = [row[0] for row in self.cursor.fetchall()]
            return cities
        except Exception as e:
            logger.error(f"Error retrieving cities: {e}")
            return []
    
    def get_properties_by_city(self, city: str) -> List[Dict[str, Any]]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT district, property_type, area, area_unit, price, price_unit, price_per_sqm, price_per_sqm_unit
            FROM properties
            WHERE city = %s
            """
            self.cursor.execute(query, (city,))
            
            properties = []
            for row in self.cursor.fetchall():
                # Format numbers to remove .0 decimal points
                area = int(row[2]) if row[2] == int(row[2]) else row[2]
                price = int(row[4]) if row[4] == int(row[4]) else row[4]
                price_per_sqm = int(row[6]) if row[6] == int(row[6]) else row[6]
                
                property_data = {
                    "квартал": row[0],
                    "тип": row[1],
                    "площ": f"{area} {row[3]}",
                    "цена": f"{price} {row[5]}",
                    "цена на квадратен метър": f"{price_per_sqm} {row[7]}"
                }
                properties.append(property_data)
            
            return properties
        except Exception as e:
            logger.error(f"Error retrieving properties for city {city}: {e}")
            return []
    
    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("MySQL connection closed")

class SQLiteConnector(DBConnector):
    """SQLite database connector"""
    
    def __init__(self, database_file: str):
        self.database_file = database_file
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        try:
            import sqlite3
            self.connection = sqlite3.connect(self.database_file)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to SQLite database: {self.database_file}")
        except ImportError:
            logger.error("sqlite3 module not found. It should be included in standard Python installation.")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            raise
    
    def get_cities(self) -> List[str]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT DISTINCT city
            FROM properties
            ORDER BY city
            """
            self.cursor.execute(query)
            cities = [row[0] for row in self.cursor.fetchall()]
            return cities
        except Exception as e:
            logger.error(f"Error retrieving cities: {e}")
            return []
    
    def get_properties_by_city(self, city: str) -> List[Dict[str, Any]]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT district, property_type, area, area_unit, price, price_unit, price_per_sqm, price_per_sqm_unit
            FROM properties
            WHERE city = ?
            """
            self.cursor.execute(query, (city,))
            
            properties = []
            for row in self.cursor.fetchall():
                # Format numbers to remove .0 decimal points
                area = int(row[2]) if row[2] == int(row[2]) else row[2]
                price = int(row[4]) if row[4] == int(row[4]) else row[4]
                price_per_sqm = int(row[6]) if row[6] == int(row[6]) else row[6]
                
                property_data = {
                    "квартал": row[0],
                    "тип": row[1],
                    "площ": f"{area} {row[3]}",
                    "цена": f"{price} {row[5]}",
                    "цена на квадратен метър": f"{price_per_sqm} {row[7]}"
                }
                properties.append(property_data)
            
            return properties
        except Exception as e:
            logger.error(f"Error retrieving properties for city {city}: {e}")
            return []
    
    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("SQLite connection closed")

class SQLServerConnector(DBConnector):
    """Microsoft SQL Server database connector"""
    
    def __init__(self, server: str, database: str, user: str, password: str):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
    
    def connect(self) -> None:
        try:
            import pyodbc
            self.connection = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};'
                f'DATABASE={self.database};UID={self.user};PWD={self.password}'
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to SQL Server database")
        except ImportError:
            logger.error("pyodbc module not found. Please install it using: pip install pyodbc")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server database: {e}")
            raise
    
    def get_cities(self) -> List[str]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT DISTINCT city
            FROM properties
            ORDER BY city
            """
            self.cursor.execute(query)
            cities = [row[0] for row in self.cursor.fetchall()]
            return cities
        except Exception as e:
            logger.error(f"Error retrieving cities: {e}")
            return []
    
    def get_properties_by_city(self, city: str) -> List[Dict[str, Any]]:
        if not self.cursor:
            self.connect()
        
        try:
            # Customize this query based on your database schema
            query = """
            SELECT district, property_type, area, area_unit, price, price_unit, price_per_sqm, price_per_sqm_unit
            FROM properties
            WHERE city = ?
            """
            self.cursor.execute(query, (city,))
            
            properties = []
            for row in self.cursor.fetchall():
                # Format numbers to remove .0 decimal points
                area = int(row[2]) if row[2] == int(row[2]) else row[2]
                price = int(row[4]) if row[4] == int(row[4]) else row[4]
                price_per_sqm = int(row[6]) if row[6] == int(row[6]) else row[6]
                
                property_data = {
                    "квартал": row[0],
                    "тип": row[1],
                    "площ": f"{area} {row[3]}",
                    "цена": f"{price} {row[5]}",
                    "цена на квадратен метър": f"{price_per_sqm} {row[7]}"
                }
                properties.append(property_data)
            
            return properties
        except Exception as e:
            logger.error(f"Error retrieving properties for city {city}: {e}")
            return []
    
    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("SQL Server connection closed")

def create_connector(db_type: str, config: Dict[str, Any]) -> DBConnector:
    """Factory function to create the appropriate database connector"""
    
    if db_type.lower() == 'postgresql':
        return PostgreSQLConnector(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            database=config.get('database', ''),
            user=config.get('user', ''),
            password=config.get('password', '')
        )
    elif db_type.lower() == 'mysql':
        return MySQLConnector(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            database=config.get('database', ''),
            user=config.get('user', ''),
            password=config.get('password', '')
        )
    elif db_type.lower() == 'sqlite':
        return SQLiteConnector(database_file=config.get('database_file', 'properties.db'))
    elif db_type.lower() == 'sqlserver':
        return SQLServerConnector(
            server=config.get('server', 'localhost'),
            database=config.get('database', ''),
            user=config.get('user', ''),
            password=config.get('password', '')
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def fetch_and_format_data(connector: DBConnector) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch data from the database and format it into the required JSON structure"""
    
    connector.connect()
    
    try:
        cities = connector.get_cities()
        result = {}
        
        for city in cities:
            properties = connector.get_properties_by_city(city)
            if properties:
                result[city] = properties
        
        return result
    finally:
        connector.close()

def save_to_json(data: Dict[str, Any], output_file: str) -> None:
    """Save the formatted data to a JSON file"""
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data successfully saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving data to {output_file}: {e}")
        raise

def load_config(config_file: str) -> Dict[str, Any]:
    """Load database configuration from a JSON file"""
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config from {config_file}: {e}")
        raise

def main():
    """Main function to execute the database to JSON conversion process"""
    
    parser = argparse.ArgumentParser(description='Extract property data from database and save as JSON')
    parser.add_argument('--config', default='db_config.json', help='Path to database configuration file')
    parser.add_argument('--output', default='input.json', help='Output JSON file path')
    args = parser.parse_args()
    
    try:
        # Load database configuration
        config = load_config(args.config)
        
        # Create appropriate database connector
        db_type = config.get('type', '')
        db_config = config.get('connection', {})
        connector = create_connector(db_type, db_config)
        
        # Fetch and format the data
        data = fetch_and_format_data(connector)
        
        # Save the data to JSON file
        save_to_json(data, args.output)
        
        logger.info("Database to JSON conversion completed successfully")
    except Exception as e:
        logger.error(f"Error during database to JSON conversion: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 