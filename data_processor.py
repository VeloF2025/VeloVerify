"""
VeloVerify Data Processor
Core module for processing pole permissions data with validation and quality control.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import logging
from typing import Dict, List, Tuple, Optional
import chardet

class DataProcessor:
    """Main data processing class for pole permissions data."""
    
    def __init__(self, progress_callback=None):
        """Initialize the data processor with optional progress callback."""
        self.progress_callback = progress_callback
        self.logger = self._setup_logging()
        self.required_columns = [
            'Property ID', '1map NAD ID', 'Pole Number', 'Drop Number', 'Stand Number',
            'Status', 'Flow Name Groups', 'Site', 'Sections', 'PONs', 'Location Address',
            'Latitude', 'Longitude', 'Field Agent Name (pole permission)', 
            'Latitude & Longitude', 'lst_mod_by', 'lst_mod_dt'
        ]
        self.processing_stats = {}
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('veloverify.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _update_progress(self, step: str, percentage: int = 0):
        """Update progress if callback is provided."""
        if self.progress_callback:
            self.progress_callback(step, percentage)
        self.logger.info(f"{step} - {percentage}%")
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding, defaulting to cp1252 for CSV files."""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
            # Default to cp1252 for CSV files as specified
            if encoding is None or encoding.lower() not in ['utf-8', 'utf-16']:
                encoding = 'cp1252'
                
            self.logger.info(f"Detected encoding: {encoding}")
            return encoding
        except Exception as e:
            self.logger.warning(f"Encoding detection failed: {e}. Using cp1252")
            return 'cp1252'
    
    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Load CSV data with proper encoding detection."""
        self._update_progress("Loading CSV file...", 10)
        
        encoding = self.detect_encoding(file_path)
        
        try:
            # Try primary encoding
            df = pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            try:
                # Fallback to utf-8
                df = pd.read_csv(file_path, encoding='utf-8')
                self.logger.info("Fallback to UTF-8 encoding successful")
            except UnicodeDecodeError:
                # Final fallback with error handling
                df = pd.read_csv(file_path, encoding='cp1252', errors='replace')
                self.logger.warning("Using cp1252 with error replacement")
        
        self.logger.info(f"Loaded {len(df)} total records")
        self.processing_stats['total_input_records'] = len(df)
        
        return df
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """Validate that all required columns are present."""
        self._update_progress("Validating columns...", 15)
        
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info("All required columns present")
        return True
    
    def filter_pole_permissions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter data to include only pole permission entries."""
        self._update_progress("Filtering pole permissions...", 25)
        
        # Create boolean mask for pole permissions
        pole_permission_mask = df['Flow Name Groups'].str.contains(
            'Pole Permission: Approved', 
            case=False, 
            na=False
        )
        
        # Exclude Home Sign Ups unless they also have Pole Permission
        home_signup_mask = df['Flow Name Groups'].str.contains(
            'Home Sign Ups', 
            case=False, 
            na=False
        )
        
        # Include if has Pole Permission OR (has Home Sign Ups AND Pole Permission)
        filtered_df = df[
            pole_permission_mask | 
            (home_signup_mask & pole_permission_mask)
        ].copy()
        
        self.logger.info(f"Filtered to {len(filtered_df)} pole permission records")
        self.processing_stats['pole_permission_records'] = len(filtered_df)
        
        return filtered_df
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats found in the data."""
        if pd.isna(date_str) or not date_str:
            return None
        
        # Handle string conversion
        date_str = str(date_str).strip()
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d %H:%M:%S.%f%z',  # ISO with timezone
            '%Y-%m-%d %H:%M:%S.%f',    # ISO without timezone
            '%Y-%m-%d %H:%M:%S',       # ISO simple
            '%a %b %d %Y %H:%M:%S GMT%z',  # JavaScript format
            '%Y-%m-%d',                # Date only
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try pandas parsing as fallback
        try:
            return pd.to_datetime(date_str)
        except:
            self.logger.warning(f"Could not parse date: {date_str}")
            return None
    
    def get_week_ending_sunday(self, date: datetime) -> datetime:
        """Calculate the week ending Sunday for a given date."""
        if not isinstance(date, datetime):
            return None
        
        day = date.weekday()  # Monday = 0, Sunday = 6
        days_until_sunday = (6 - day) % 7
        
        # If it's already Sunday, use the same day
        if days_until_sunday == 0 and date.weekday() == 6:
            return date.replace(hour=23, minute=59, second=59, microsecond=0)
        
        # Otherwise, find next Sunday
        if days_until_sunday == 0:
            days_until_sunday = 7
        
        week_ending = date + timedelta(days=days_until_sunday)
        return week_ending.replace(hour=23, minute=59, second=59, microsecond=0)
    
    def quality_control_checks(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Perform quality control checks and separate problematic data."""
        self._update_progress("Performing quality control checks...", 40)
        
        results = {
            'clean_data': df.copy(),
            'no_pole_allocated': pd.DataFrame(),
            'agent_data_mismatches': pd.DataFrame(),
            'date_parse_errors': pd.DataFrame()
        }
        
        # Check for missing pole numbers
        no_pole_mask = df['Pole Number'].isna() | (df['Pole Number'] == '') | (df['Pole Number'] == 'nan')
        if no_pole_mask.any():
            results['no_pole_allocated'] = df[no_pole_mask].copy()
            results['clean_data'] = results['clean_data'][~no_pole_mask]
        
        # Check agent data mismatches
        agent_name_exists = results['clean_data']['Field Agent Name (pole permission)'].notna()
        lst_mod_by_no_email = ~results['clean_data']['lst_mod_by'].str.contains('@', na=True)
        mismatch_mask = agent_name_exists & lst_mod_by_no_email
        
        if mismatch_mask.any():
            results['agent_data_mismatches'] = results['clean_data'][mismatch_mask].copy()
            # Note: Keep these in clean_data for now, just flag them
        
        # Parse dates and handle errors
        results['clean_data']['parsed_date'] = results['clean_data']['lst_mod_dt'].apply(self.parse_date)
        date_error_mask = results['clean_data']['parsed_date'].isna() & results['clean_data']['lst_mod_dt'].notna()
        
        if date_error_mask.any():
            results['date_parse_errors'] = results['clean_data'][date_error_mask].copy()
            # Remove records with unparseable dates
            results['clean_data'] = results['clean_data'][~date_error_mask]
        
        self.logger.info(f"Quality control complete:")
        self.logger.info(f"  - Clean data: {len(results['clean_data'])}")
        self.logger.info(f"  - No pole allocated: {len(results['no_pole_allocated'])}")
        self.logger.info(f"  - Agent mismatches: {len(results['agent_data_mismatches'])}")
        self.logger.info(f"  - Date parse errors: {len(results['date_parse_errors'])}")
        
        return results
    
    def remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Remove duplicates keeping the earliest entry for each pole."""
        self._update_progress("Removing duplicates...", 60)
        
        # Sort by pole number and date to ensure earliest comes first
        df_sorted = df.sort_values(['Pole Number', 'parsed_date'])
        
        # Keep first occurrence (earliest date) for each pole
        unique_df = df_sorted.drop_duplicates(subset=['Pole Number'], keep='first')
        
        # Get duplicates for separate sheet
        duplicate_mask = df_sorted.index.isin(unique_df.index)
        duplicates_df = df_sorted[~duplicate_mask].copy()
        
        self.logger.info(f"Removed {len(duplicates_df)} duplicate entries")
        self.logger.info(f"Remaining unique poles: {len(unique_df)}")
        
        self.processing_stats['unique_poles'] = len(unique_df)
        self.processing_stats['duplicates_removed'] = len(duplicates_df)
        
        return unique_df, duplicates_df
    
    def group_by_weeks(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Group data by week ending Sunday."""
        self._update_progress("Grouping by weeks...", 75)
        
        # Calculate week ending for each record
        df['week_ending'] = df['parsed_date'].apply(self.get_week_ending_sunday)
        
        # Remove records with invalid week calculations
        valid_weeks = df['week_ending'].notna()
        df = df[valid_weeks]
        
        # Group by week ending
        weekly_groups = {}
        for week_ending, group in df.groupby('week_ending'):
            if week_ending:
                week_str = week_ending.strftime('Week_Ending_%Y-%m-%d')
                weekly_groups[week_str] = group.copy()
        
        # Sort weeks chronologically
        sorted_weeks = dict(sorted(weekly_groups.items(), 
                                 key=lambda x: datetime.strptime(x[0].split('_')[-1], '%Y-%m-%d')))
        
        self.logger.info(f"Created {len(sorted_weeks)} weekly groups")
        for week, data in sorted_weeks.items():
            self.logger.info(f"  - {week}: {len(data)} entries")
        
        self.processing_stats['weekly_sheets'] = len(sorted_weeks)
        
        return sorted_weeks
    
    def create_processing_summary(self) -> pd.DataFrame:
        """Create a summary of processing statistics."""
        summary_data = []
        
        for key, value in self.processing_stats.items():
            summary_data.append({
                'Metric': key.replace('_', ' ').title(),
                'Value': value
            })
        
        # Add processing timestamp
        summary_data.append({
            'Metric': 'Processing Timestamp',
            'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return pd.DataFrame(summary_data)
    
    def process_data(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Main method to process the CSV data and return all sheets."""
        try:
            self.logger.info(f"Starting data processing for: {file_path}")
            
            # Load and validate data
            df = self.load_csv_data(file_path)
            self.validate_columns(df)
            
            # Filter for pole permissions
            filtered_df = self.filter_pole_permissions(df)
            
            # Quality control checks
            qc_results = self.quality_control_checks(filtered_df)
            clean_df = qc_results['clean_data']
            
            # Remove duplicates
            unique_df, duplicates_df = self.remove_duplicates(clean_df)
            
            # Group by weeks
            weekly_groups = self.group_by_weeks(unique_df)
            
            # Prepare final results
            results = {}
            
            # Add weekly sheets
            results.update(weekly_groups)
            
            # Add quality control sheets
            if len(duplicates_df) > 0:
                results['Duplicate_Poles_Removed'] = duplicates_df
            if len(qc_results['no_pole_allocated']) > 0:
                results['No_Pole_Allocated'] = qc_results['no_pole_allocated']
            if len(qc_results['agent_data_mismatches']) > 0:
                results['Agent_Data_Mismatches'] = qc_results['agent_data_mismatches']
            if len(qc_results['date_parse_errors']) > 0:
                results['Date_Parse_Errors'] = qc_results['date_parse_errors']
            
            # Add processing summary
            results['Processing_Summary'] = self.create_processing_summary()
            
            self._update_progress("Processing complete!", 100)
            self.logger.info("Data processing completed successfully")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {str(e)}")
            self._update_progress(f"Error: {str(e)}", 0)
            raise 