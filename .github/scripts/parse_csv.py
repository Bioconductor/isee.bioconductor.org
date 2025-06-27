#!/usr/bin/env python3
"""
CSV Parser for iSEE deployment configuration.

This script parses the config.csv file and extracts the required fields
for deploying iSEE subdomains: ID, datasetURI, and configURI.

Usage:
    python3 parse_csv.py config.csv
"""

import csv
import sys
import os

def parse_config_csv(csv_file):
    """
    Parse the config CSV file and extract required fields.
    
    Args:
        csv_file (str): Path to the CSV file
        
    Yields:
        tuple: (ID, datasetURI, configURI) for each valid row
    """
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Read and validate header
            try:
                header = next(reader)
            except StopIteration:
                print("Error: CSV file is empty", file=sys.stderr)
                sys.exit(1)
            
            row_number = 1  # Start from 1 (header is row 0)
            
            for row in reader:
                row_number += 1
                
                # Skip empty rows
                if not row or all(cell.strip() == '' for cell in row):
                    continue
                
                # Ensure we have enough columns
                if len(row) < 7:
                    print(f"Warning: Row {row_number} has insufficient columns ({len(row)}), skipping", 
                          file=sys.stderr)
                    continue
                
                # Extract required fields (0-indexed)
                # Based on actual CSV data: configURI is in column 6 (configTitle field)
                ID = row[0].strip()
                datasetURI = row[3].strip()  # Column 4: datasetURI
                configURI = row[6].strip()   # Column 7: configTitle field contains the actual configURI
                
                # Validate required fields are not empty
                if not ID:
                    print(f"Warning: Row {row_number} has empty ID, skipping", file=sys.stderr)
                    continue
                
                if not datasetURI:
                    print(f"Warning: Row {row_number} has empty datasetURI, skipping", file=sys.stderr)
                    continue
                
                if not configURI:
                    print(f"Warning: Row {row_number} has empty configURI, skipping", file=sys.stderr)
                    continue
                
                yield (ID, datasetURI, configURI)
                
    except FileNotFoundError:
        print(f"Error: Could not open file '{csv_file}'", file=sys.stderr)
        sys.exit(1)
    except csv.Error as e:
        print(f"Error parsing CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to process command line arguments and parse CSV."""
    if len(sys.argv) != 2:
        print("Usage: python3 parse_csv.py <config.csv>", file=sys.stderr)
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Parse CSV and output results
    for ID, datasetURI, configURI in parse_config_csv(csv_file):
        # Output in pipe-delimited format for shell processing
        print(f"{ID}|{datasetURI}|{configURI}")

if __name__ == "__main__":
    main()
