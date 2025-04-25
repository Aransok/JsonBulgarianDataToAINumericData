#!/usr/bin/env python
"""
Property Listings CLI
--------------------
Command Line Interface for the Property Listings Application.
Provides utilities to work with property data from various sources.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, List, Optional
import time
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# Import application modules
import create_sample_db
import db_to_json
import main as pdf_generator

# Initialize colorama
colorama.init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PropertyCLI:
    """Main CLI class for Property Listings Application"""
    
    def __init__(self):
        """Initialize the CLI application"""
        self.parser = argparse.ArgumentParser(
            description='Property Listings CLI Application',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python property_cli.py create-db --output properties.db
  python property_cli.py db-to-json --config db_config.json --output input.json
  python property_cli.py generate-pdf --input input.json --output properties.pdf
  python property_cli.py full-process --db-type sqlite --db-file properties.db --output properties.pdf
""")
        
        # Create subparsers for different commands
        self.subparsers = self.parser.add_subparsers(dest='command', help='Commands')
        self._setup_create_db_parser()
        self._setup_db_to_json_parser()
        self._setup_generate_pdf_parser()
        self._setup_full_process_parser()
        self._setup_list_db_types_parser()
    
    def _setup_create_db_parser(self):
        """Set up the parser for the create-db command"""
        create_db_parser = self.subparsers.add_parser('create-db', help='Create a sample SQLite database')
        create_db_parser.add_argument('--output', default='properties.db', help='Output database file path')
    
    def _setup_db_to_json_parser(self):
        """Set up the parser for the db-to-json command"""
        db_to_json_parser = self.subparsers.add_parser('db-to-json', help='Convert database to JSON')
        db_to_json_parser.add_argument('--config', default='db_config.json', help='Database configuration file path')
        db_to_json_parser.add_argument('--output', default='input.json', help='Output JSON file path')
    
    def _setup_generate_pdf_parser(self):
        """Set up the parser for the generate-pdf command"""
        generate_pdf_parser = self.subparsers.add_parser('generate-pdf', help='Generate PDF from JSON')
        generate_pdf_parser.add_argument('--input', default='input.json', help='Input JSON file path')
        generate_pdf_parser.add_argument('--output', default='property_listings_en.pdf', help='Output PDF file path')
    
    def _setup_full_process_parser(self):
        """Set up the parser for the full-process command"""
        full_process_parser = self.subparsers.add_parser('full-process', help='Run the full database to PDF process')
        
        # Database options
        db_group = full_process_parser.add_argument_group('Database options')
        db_group.add_argument('--db-type', choices=['sqlite', 'postgresql', 'mysql', 'sqlserver', 'mongodb'],
                           default='sqlite', help='Database type')
        db_group.add_argument('--db-file', default='properties.db', help='Database file (for SQLite)')
        db_group.add_argument('--db-host', default='localhost', help='Database host (for PostgreSQL/MySQL/SQL Server)')
        db_group.add_argument('--db-port', type=int, help='Database port')
        db_group.add_argument('--db-name', help='Database name (for PostgreSQL/MySQL/SQL Server)')
        db_group.add_argument('--db-user', help='Database user (for PostgreSQL/MySQL/SQL Server)')
        db_group.add_argument('--db-password', help='Database password (for PostgreSQL/MySQL/SQL Server)')
        db_group.add_argument('--mongodb-uri', default='mongodb://localhost:27017', 
                           help='MongoDB connection URI (for MongoDB)')
        db_group.add_argument('--mongodb-db', default='properties', help='MongoDB database name (for MongoDB)')
        db_group.add_argument('--mongodb-collection', default='listings', 
                           help='MongoDB collection name (for MongoDB)')
        
        # Output options
        output_group = full_process_parser.add_argument_group('Output options')
        output_group.add_argument('--temp-json', default='input.json', help='Temporary JSON file path')
        output_group.add_argument('--output', default='property_listings_en.pdf', help='Output PDF file path')
        
        # Process options
        process_group = full_process_parser.add_argument_group('Process options')
        process_group.add_argument('--skip-db-to-json', action='store_true', 
                                help='Skip database to JSON conversion (use existing JSON)')
        process_group.add_argument('--skip-json-to-pdf', action='store_true',
                                help='Skip JSON to PDF conversion (generate JSON only)')
    
    def _setup_list_db_types_parser(self):
        """Set up the parser for the list-db-types command"""
        list_db_types_parser = self.subparsers.add_parser('list-db-types', help='List supported database types')
    
    def _create_db_config(self, args) -> Dict[str, Any]:
        """Create a database configuration dictionary from command-line arguments"""
        config = {
            "type": args.db_type,
            "connection": {}
        }
        
        if args.db_type == "sqlite":
            config["connection"]["database_file"] = args.db_file
        elif args.db_type == "mongodb":
            config["connection"]["connection_string"] = args.mongodb_uri
            config["connection"]["database"] = args.mongodb_db
            config["connection"]["collection"] = args.mongodb_collection
        else:  # PostgreSQL, MySQL, SQL Server
            config["connection"]["host"] = args.db_host
            if args.db_port:
                config["connection"]["port"] = args.db_port
            if args.db_name:
                config["connection"]["database"] = args.db_name
            if args.db_user:
                config["connection"]["user"] = args.db_user
            if args.db_password:
                config["connection"]["password"] = args.db_password
        
        return config
    
    def run(self):
        """Run the CLI application based on the command-line arguments"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        # Execute the appropriate command
        if args.command == 'create-db':
            return self._run_create_db(args)
        elif args.command == 'db-to-json':
            return self._run_db_to_json(args)
        elif args.command == 'generate-pdf':
            return self._run_generate_pdf(args)
        elif args.command == 'full-process':
            return self._run_full_process(args)
        elif args.command == 'list-db-types':
            return self._run_list_db_types()
        else:
            self.parser.print_help()
            return 1
    
    def _run_create_db(self, args):
        """Run the create-db command"""
        print(f"{Fore.CYAN}Creating sample SQLite database...{Style.RESET_ALL}")
        
        try:
            # Show progress bar
            with tqdm(total=100, desc="Creating database", ncols=100) as pbar:
                pbar.update(10)
                
                # Remove existing database if it exists
                if os.path.exists(args.output):
                    os.remove(args.output)
                    pbar.update(10)
                
                # Create database
                create_sample_db.create_database(args.output)
                pbar.update(80)
            
            print(f"{Fore.GREEN}Database created successfully: {args.output}{Style.RESET_ALL}")
            return 0
        except Exception as e:
            print(f"{Fore.RED}Error creating database: {e}{Style.RESET_ALL}")
            return 1
    
    def _run_db_to_json(self, args):
        """Run the db-to-json command"""
        print(f"{Fore.CYAN}Converting database to JSON...{Style.RESET_ALL}")
        
        try:
            # Show progress bar
            with tqdm(total=100, desc="Converting database", ncols=100) as pbar:
                pbar.update(10)
                
                # Load database configuration
                config = db_to_json.load_config(args.config)
                pbar.update(20)
                
                # Create appropriate database connector
                db_type = config.get('type', '')
                db_config = config.get('connection', {})
                connector = db_to_json.create_connector(db_type, db_config)
                pbar.update(20)
                
                # Fetch and format the data
                data = db_to_json.fetch_and_format_data(connector)
                pbar.update(30)
                
                # Save the data to JSON file
                db_to_json.save_to_json(data, args.output)
                pbar.update(20)
            
            print(f"{Fore.GREEN}Database to JSON conversion completed successfully: {args.output}{Style.RESET_ALL}")
            return 0
        except Exception as e:
            print(f"{Fore.RED}Error converting database to JSON: {e}{Style.RESET_ALL}")
            return 1
    
    def _run_generate_pdf(self, args):
        """Run the generate-pdf command"""
        print(f"{Fore.CYAN}Generating PDF from JSON...{Style.RESET_ALL}")
        
        try:
            # Show progress bar
            with tqdm(total=100, desc="Generating PDF", ncols=100) as pbar:
                pbar.update(10)
                
                # Load data
                print(f"{Fore.YELLOW}Loading data from {args.input}...{Style.RESET_ALL}")
                data = pdf_generator.load_data(args.input)
                pbar.update(20)
                
                # Translate data
                print(f"{Fore.YELLOW}Translating data...{Style.RESET_ALL}")
                translated_data = pdf_generator.translate_data(data)
                pbar.update(40)
                
                # Generate PDF
                print(f"{Fore.YELLOW}Generating PDF...{Style.RESET_ALL}")
                pdf_generator.generate_pdf(translated_data, args.output)
                pbar.update(30)
            
            print(f"{Fore.GREEN}PDF generated successfully: {args.output}{Style.RESET_ALL}")
            return 0
        except Exception as e:
            print(f"{Fore.RED}Error generating PDF: {e}{Style.RESET_ALL}")
            return 1
    
    def _run_full_process(self, args):
        """Run the full-process command"""
        print(f"{Fore.CYAN}Running full database to PDF process...{Style.RESET_ALL}")
        
        try:
            # Prepare database to JSON conversion
            if not args.skip_db_to_json:
                print(f"{Fore.YELLOW}Step 1/2: Converting database to JSON...{Style.RESET_ALL}")
                
                # Create temporary config file
                temp_config_file = "temp_db_config.json"
                config = self._create_db_config(args)
                
                with open(temp_config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                # Convert database to JSON
                db_args = argparse.Namespace(config=temp_config_file, output=args.temp_json)
                result = self._run_db_to_json(db_args)
                
                # Clean up temporary config file
                if os.path.exists(temp_config_file):
                    os.remove(temp_config_file)
                
                if result != 0:
                    return result
            
            # Skip JSON to PDF conversion if requested
            if args.skip_json_to_pdf:
                print(f"{Fore.GREEN}Full process completed successfully (JSON only){Style.RESET_ALL}")
                return 0
            
            # Convert JSON to PDF
            print(f"{Fore.YELLOW}Step 2/2: Converting JSON to PDF...{Style.RESET_ALL}")
            pdf_args = argparse.Namespace(input=args.temp_json, output=args.output)
            result = self._run_generate_pdf(pdf_args)
            
            if result == 0:
                print(f"{Fore.GREEN}Full process completed successfully: {args.output}{Style.RESET_ALL}")
            
            return result
        except Exception as e:
            print(f"{Fore.RED}Error during full process: {e}{Style.RESET_ALL}")
            return 1
    
    def _run_list_db_types(self):
        """Run the list-db-types command"""
        db_types = [
            ("sqlite", "SQLite", "Lightweight file-based database"),
            ("postgresql", "PostgreSQL", "Advanced open-source relational database"),
            ("mysql", "MySQL", "Popular open-source relational database"),
            ("sqlserver", "SQL Server", "Microsoft's relational database product"),
            ("mongodb", "MongoDB", "NoSQL document database")
        ]
        
        print(f"{Fore.CYAN}Supported database types:{Style.RESET_ALL}")
        print()
        
        for db_id, db_name, db_desc in db_types:
            print(f"{Fore.GREEN}{db_id}{Style.RESET_ALL} - {Fore.YELLOW}{db_name}{Style.RESET_ALL}: {db_desc}")
        
        return 0

if __name__ == "__main__":
    cli = PropertyCLI()
    exit(cli.run()) 