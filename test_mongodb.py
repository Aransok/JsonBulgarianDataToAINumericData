#!/usr/bin/env python
"""
Test script for MongoDB connector
"""

import json
import logging
import db_to_json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test MongoDB connector functionality"""
    # Test configuration
    config = {
        "connection_string": "mongodb://localhost:27017",
        "database": "test_properties",
        "collection": "listings"
    }
    
    try:
        # Create MongoDB connector
        print("Creating MongoDB connector...")
        connector = db_to_json.MongoDBConnector(
            connection_string=config["connection_string"],
            database=config["database"],
            collection=config["collection"]
        )
        
        # Test connection
        print("Testing connection to MongoDB...")
        connector.connect()
        print("Successfully connected to MongoDB")
        
        # Close connection
        connector.close()
        print("Connection closed successfully")
        
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please make sure pymongo is installed: pip install pymongo")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed.") 