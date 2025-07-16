"""
Simple script to compare two Excel or CSV files
"""

import pandas as pd
import os
from pathlib import Path
import sys

def load_file(file_path):
    """Load an Excel or CSV file."""
    print(f"Loading file: {file_path}")
    try:
        if file_path.lower().endswith('.csv'):
            return pd.read_csv(file_path, encoding='utf-8', on_bad_lines='warn')
        else:
            return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        return None

def compare_files(file_a_path, file_b_path, key_columns=None, output_dir='.'):
    """Compare two files and export the differences."""
    # Load files
    df_a = load_file(file_a_path)
    df_b = load_file(file_b_path)
    
    if df_a is None or df_b is None:
        print("Failed to load one or both files")
        return
    
    print(f"\nSheet A has {len(df_a)} rows")
    print(f"Sheet B has {len(df_b)} rows")
    
    # If no key columns specified, use all common columns
    if not key_columns:
        key_columns = list(set(df_a.columns) & set(df_b.columns))
        print(f"\nUsing common columns as keys: {', '.join(key_columns)}")
    
    # Verify key columns exist in both sheets
    for col in key_columns:
        if col not in df_a.columns or col not in df_b.columns:
            print(f"\nError: Key column '{col}' not found in both sheets")
            return
    
    # Create unique identifiers for each row
    df_a['_merge_key'] = df_a[key_columns].astype(str).agg('-'.join, axis=1)
    df_b['_merge_key'] = df_b[key_columns].astype(str).agg('-'.join, axis=1)
    
    # Find rows unique to each sheet
    keys_only_in_a = set(df_a['_merge_key']) - set(df_b['_merge_key'])
    keys_only_in_b = set(df_b['_merge_key']) - set(df_a['_merge_key'])
    
    # Get the full rows that are unique to each sheet
    rows_only_in_a = df_a[df_a['_merge_key'].isin(keys_only_in_a)].drop('_merge_key', axis=1)
    rows_only_in_b = df_b[df_b['_merge_key'].isin(keys_only_in_b)].drop('_merge_key', axis=1)
    
    # Clean up temporary column
    df_a.drop('_merge_key', axis=1, inplace=True)
    df_b.drop('_merge_key', axis=1, inplace=True)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Export results
    if len(rows_only_in_a) > 0:
        output_file = output_path / 'unique_to_file_a.xlsx'
        rows_only_in_a.to_excel(output_file, index=False)
        print(f"\nExported {len(rows_only_in_a)} rows unique to file A: {output_file}")
    
    if len(rows_only_in_b) > 0:
        output_file = output_path / 'unique_to_file_b.xlsx'
        rows_only_in_b.to_excel(output_file, index=False)
        print(f"Exported {len(rows_only_in_b)} rows unique to file B: {output_file}")
    
    # Export summary
    summary = pd.DataFrame([{
        'Total Rows in File A': len(df_a),
        'Total Rows in File B': len(df_b),
        'Rows Only in File A': len(rows_only_in_a),
        'Rows Only in File B': len(rows_only_in_b),
        'Key Columns Used': ', '.join(key_columns)
    }])
    
    summary_file = output_path / 'comparison_summary.xlsx'
    summary.to_excel(summary_file, index=False)
    print(f"Exported comparison summary: {summary_file}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("python compare_files.py file_a file_b [key_columns] [output_dir]")
        print("\nExample:")
        print('python compare_files.py data1.csv data2.csv "ID,Name" results')
        return
    
    file_a = sys.argv[1]
    file_b = sys.argv[2]
    
    key_columns = None
    if len(sys.argv) > 3:
        key_columns = [col.strip() for col in sys.argv[3].split(',')]
    
    output_dir = '.'
    if len(sys.argv) > 4:
        output_dir = sys.argv[4]
    
    compare_files(file_a, file_b, key_columns, output_dir)

if __name__ == '__main__':
    main() 