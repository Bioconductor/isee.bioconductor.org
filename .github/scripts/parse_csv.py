#!/usr/bin/env python3
"""
CSV Parser for iSEE deployment configuration.

This script parses the config-dataset.csv and config-initial.csv 
files and extracts the required fields
for deploying iSEE subdomains: ID, datasetURI, and configURI.

Usage:
    python3 parse_csv.py config-dataset.csv config-initial.csv
"""

import csv
import sys
import os

def parse_config_csv(csv_file, columns_to_extract, n_columns):
    """
    Parse the config CSV file and extract required fields.
    
    Args:
        csv_file (str): Path to the CSV file
        columns_to_extract (list[int]): List of columns to extract
        n_columns: int: Number of columns to expect in the csv file
        
    Yields:
        tuple with values from the indicated columns for each valid row
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
                if len(row) < n_columns:
                    print(f"Warning: Row {row_number} has insufficient columns ({len(row)}), skipping", 
                          file=sys.stderr)
                    continue
                
                # Extract required fields (0-indexed)
                values = [row[k].strip() for k in columns_to_extract]
                for k in range(len(columns_to_extract)):
                    if not values[k]:
                        print(f"Warning: Row {row_number} has empty value {k}, skipping", file=sys.stderr)
                                
                yield tuple(values)
                
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
    """Main function to process command line arguments and parse CSVs."""
    if len(sys.argv) != 3:
        print("Usage: python3 parse_csv.py <config-dataset.csv> <config-initial.csv>", file=sys.stderr)
        sys.exit(1)
    
    csv_data = sys.argv[1]
    csv_initial = sys.argv[2]

    datasetMapping = {}
    for datasetID, datasetURI in parse_config_csv(csv_data, [0, 2], 4):
        datasetMapping[datasetID] = datasetURI
    
    # Parse CSV and output results
    for ID, datasetID, configURI in parse_config_csv(csv_initial, [0, 1, 4], 7):
        datasetURI = datasetMapping[datasetID]
        # Output in pipe-delimited format for shell processing
        print(f"{ID}#@#{datasetURI}#@#{configURI}")

if __name__ == "__main__":
    main()
