"""
VeloCompare - Compare two Excel sheets and identify differences
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from pathlib import Path

class VeloCompare:
    """Compare two Excel sheets and identify differences between them."""
    
    def __init__(self):
        """Initialize the VeloCompare with logging setup."""
        self.logger = self._setup_logging()
        self.sheet_a = None
        self.sheet_b = None
        self.comparison_results = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('velocompare.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def load_sheets(self, file_a_path: str, file_b_path: str) -> bool:
        """
        Load the two sheets for comparison.
        
        Args:
            file_a_path: Path to the first file (Sheet A)
            file_b_path: Path to the second file (Sheet B)
            
        Returns:
            bool: True if both sheets loaded successfully
        """
        try:
            self.logger.info(f"Loading Sheet A from: {file_a_path}")
            if file_a_path.lower().endswith('.csv'):
                self.sheet_a = pd.read_csv(file_a_path, encoding='utf-8', on_bad_lines='warn')
            else:
                self.sheet_a = pd.read_excel(file_a_path)
            self.logger.info(f"Sheet A loaded with {len(self.sheet_a)} rows")
            
            self.logger.info(f"Loading Sheet B from: {file_b_path}")
            if file_b_path.lower().endswith('.csv'):
                self.sheet_b = pd.read_csv(file_b_path, encoding='utf-8', on_bad_lines='warn')
            else:
                self.sheet_b = pd.read_excel(file_b_path)
            self.logger.info(f"Sheet B loaded with {len(self.sheet_b)} rows")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading sheets: {str(e)}")
            return False
    
    def compare_sheets(self, key_columns: List[str] = None) -> Dict:
        """
        Compare the two loaded sheets and identify differences.
        
        Args:
            key_columns: List of column names to use as unique identifiers for rows.
                        If None, will use all common columns between sheets.
        
        Returns:
            Dict containing comparison results
        """
        if self.sheet_a is None or self.sheet_b is None:
            self.logger.error("Sheets not loaded. Call load_sheets() first.")
            return None
            
        try:
            # If no key columns specified, use all common columns
            if key_columns is None:
                key_columns = list(set(self.sheet_a.columns) & set(self.sheet_b.columns))
                self.logger.info(f"Using common columns as keys: {key_columns}")
            
            # Verify key columns exist in both sheets
            for col in key_columns:
                if col not in self.sheet_a.columns or col not in self.sheet_b.columns:
                    self.logger.error(f"Key column '{col}' not found in both sheets")
                    return None
            
            # Create unique identifiers for each row
            self.sheet_a['_merge_key'] = self.sheet_a[key_columns].astype(str).agg('-'.join, axis=1)
            self.sheet_b['_merge_key'] = self.sheet_b[key_columns].astype(str).agg('-'.join, axis=1)
            
            # Find rows unique to each sheet
            keys_only_in_a = set(self.sheet_a['_merge_key']) - set(self.sheet_b['_merge_key'])
            keys_only_in_b = set(self.sheet_b['_merge_key']) - set(self.sheet_a['_merge_key'])
            
            # Get the full rows that are unique to each sheet
            rows_only_in_a = self.sheet_a[self.sheet_a['_merge_key'].isin(keys_only_in_a)].drop('_merge_key', axis=1)
            rows_only_in_b = self.sheet_b[self.sheet_b['_merge_key'].isin(keys_only_in_b)].drop('_merge_key', axis=1)
            
            # Store results
            self.comparison_results = {
                'rows_only_in_a': rows_only_in_a,
                'rows_only_in_b': rows_only_in_b,
                'key_columns_used': key_columns,
                'total_rows_a': len(self.sheet_a),
                'total_rows_b': len(self.sheet_b),
                'unique_to_a': len(rows_only_in_a),
                'unique_to_b': len(rows_only_in_b)
            }
            
            # Clean up temporary column
            self.sheet_a.drop('_merge_key', axis=1, inplace=True)
            self.sheet_b.drop('_merge_key', axis=1, inplace=True)
            
            return self.comparison_results
            
        except Exception as e:
            self.logger.error(f"Error comparing sheets: {str(e)}")
            return None
    
    def export_results(self, output_dir: str = '.') -> bool:
        """
        Export comparison results to Excel files.
        
        Args:
            output_dir: Directory to save the output files (default: current directory)
            
        Returns:
            bool: True if export was successful
        """
        if not self.comparison_results:
            self.logger.error("No comparison results to export. Run compare_sheets() first.")
            return False
            
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Export rows unique to Sheet A
            if len(self.comparison_results['rows_only_in_a']) > 0:
                a_output = output_path / 'unique_to_sheet_a.xlsx'
                self.comparison_results['rows_only_in_a'].to_excel(a_output, index=False)
                self.logger.info(f"Exported {len(self.comparison_results['rows_only_in_a'])} rows unique to Sheet A: {a_output}")
            
            # Export rows unique to Sheet B
            if len(self.comparison_results['rows_only_in_b']) > 0:
                b_output = output_path / 'unique_to_sheet_b.xlsx'
                self.comparison_results['rows_only_in_b'].to_excel(b_output, index=False)
                self.logger.info(f"Exported {len(self.comparison_results['rows_only_in_b'])} rows unique to Sheet B: {b_output}")
            
            # Export summary
            summary = pd.DataFrame([{
                'Total Rows in Sheet A': self.comparison_results['total_rows_a'],
                'Total Rows in Sheet B': self.comparison_results['total_rows_b'],
                'Rows Only in Sheet A': self.comparison_results['unique_to_a'],
                'Rows Only in Sheet B': self.comparison_results['unique_to_b'],
                'Key Columns Used': ', '.join(self.comparison_results['key_columns_used'])
            }])
            
            summary_output = output_path / 'comparison_summary.xlsx'
            summary.to_excel(summary_output, index=False)
            self.logger.info(f"Exported comparison summary: {summary_output}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting results: {str(e)}")
            return False

def main():
    """Example usage of VeloCompare."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare two Excel sheets and identify differences')
    parser.add_argument('file_a', help='Path to first Excel file (Sheet A)')
    parser.add_argument('file_b', help='Path to second Excel file (Sheet B)')
    parser.add_argument('--key-columns', nargs='+', help='Column names to use as unique identifiers')
    parser.add_argument('--output-dir', default='.', help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Initialize and run comparison
    comparator = VeloCompare()
    
    if comparator.load_sheets(args.file_a, args.file_b):
        results = comparator.compare_sheets(args.key_columns)
        if results:
            comparator.export_results(args.output_dir)
            print("\nComparison Summary:")
            print(f"Total rows in Sheet A: {results['total_rows_a']}")
            print(f"Total rows in Sheet B: {results['total_rows_b']}")
            print(f"Rows only in Sheet A: {results['unique_to_a']}")
            print(f"Rows only in Sheet B: {results['unique_to_b']}")
            print(f"\nKey columns used: {', '.join(results['key_columns_used'])}")
            print("\nDetailed results have been exported to Excel files in the output directory.")

if __name__ == '__main__':
    main() 