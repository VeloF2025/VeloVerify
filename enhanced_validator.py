"""
Enhanced Data Validator for VeloVerify
Provides comprehensive data validation with configurable rules and detailed reporting.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

from config import get_config

class ValidationResult:
    """Class to hold validation results and errors."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.info = []
        self.stats = {}
    
    def add_error(self, message: str, row_indices: List[int] = None):
        """Add an error to the validation result."""
        self.is_valid = False
        self.errors.append({
            'message': message,
            'severity': 'error',
            'rows': row_indices or [],
            'count': len(row_indices) if row_indices else 0
        })
    
    def add_warning(self, message: str, row_indices: List[int] = None):
        """Add a warning to the validation result."""
        self.warnings.append({
            'message': message,
            'severity': 'warning',
            'rows': row_indices or [],
            'count': len(row_indices) if row_indices else 0
        })
    
    def add_info(self, message: str, value: Any = None):
        """Add informational message."""
        self.info.append({
            'message': message,
            'value': value
        })
    
    def get_summary(self) -> str:
        """Get a formatted summary of validation results."""
        summary = []
        summary.append(f"Validation Status: {'✅ PASSED' if self.is_valid else '❌ FAILED'}")
        summary.append(f"Errors: {len(self.errors)}")
        summary.append(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            summary.append("\nERRORS:")
            for error in self.errors:
                summary.append(f"  • {error['message']} ({error['count']} rows)")
        
        if self.warnings:
            summary.append("\nWARNINGS:")
            for warning in self.warnings:
                summary.append(f"  • {warning['message']} ({warning['count']} rows)")
        
        return "\n".join(summary)

class EnhancedDataValidator:
    """Enhanced data validator with configurable validation rules."""
    
    def __init__(self, config=None):
        """Initialize the validator with configuration."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Standard column names and their variations
        self.column_mappings = {
            'property_id': ['Property ID', 'PropertyID', 'Prop ID', 'property_id'],
            'nad_id': ['1map NAD ID', 'NAD ID', 'NADID', 'nad_id'],
            'pole_number': ['Pole Number', 'PoleNumber', 'Pole No', 'pole_number'],
            'drop_number': ['Drop Number', 'DropNumber', 'Drop No', 'drop_number'],
            'stand_number': ['Stand Number', 'StandNumber', 'Stand No', 'stand_number'],
            'status': ['Status', 'status'],
            'flow_name_groups': ['Flow Name Groups', 'FlowNameGroups', 'Flow Groups', 'flow_name_groups'],
            'site': ['Site', 'site'],
            'sections': ['Sections', 'sections'],
            'pons': ['PONs', 'PON', 'pons'],
            'location_address': ['Location Address', 'LocationAddress', 'Address', 'location_address'],
            'latitude': ['Latitude', 'Lat', 'latitude'],
            'longitude': ['Longitude', 'Long', 'Lng', 'longitude'],
            'agent_name': ['Field Agent Name (pole permission)', 'Agent Name', 'Field Agent', 'agent_name'],
            'lat_long': ['Latitude & Longitude', 'Lat & Long', 'Coordinates', 'lat_long'],
            'modified_by': ['lst_mod_by', 'Modified By', 'Last Modified By', 'modified_by'],
            'modified_date': ['lst_mod_dt', 'Modified Date', 'Last Modified', 'modified_date']
        }
        
        # Email validation pattern
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Coordinate validation patterns
        self.lat_pattern = re.compile(r'^-?([0-8]?[0-9]|90)(\.[0-9]+)?$')
        self.lon_pattern = re.compile(r'^-?(1[0-7][0-9]|[0-9]?[0-9])(\.[0-9]+)?$')
    
    def validate_dataframe(self, df: pd.DataFrame, source_file: str = None) -> ValidationResult:
        """Perform comprehensive validation on the dataframe."""
        result = ValidationResult()
        
        try:
            self.logger.info("Starting enhanced data validation")
            
            # Basic structure validation
            self._validate_structure(df, result)
            
            # Column validation
            self._validate_columns(df, result)
            
            # Data type validation
            self._validate_data_types(df, result)
            
            # Content validation
            self._validate_content(df, result)
            
            # Business rule validation
            self._validate_business_rules(df, result)
            
            # Generate statistics
            self._generate_statistics(df, result)
            
            self.logger.info(f"Validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
            
        except Exception as e:
            result.add_error(f"Validation failed with exception: {str(e)}")
            self.logger.error(f"Validation exception: {e}")
        
        return result
    
    def _validate_structure(self, df: pd.DataFrame, result: ValidationResult):
        """Validate basic dataframe structure."""
        # Check if dataframe is empty
        if df.empty:
            result.add_error("Dataframe is empty")
            return
        
        # Check row count
        if len(df) < 1:
            result.add_error("No data rows found")
        elif len(df) > 100000:
            result.add_warning(f"Large dataset ({len(df)} rows) may impact performance")
        
        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1)
        if empty_rows.any():
            empty_indices = df[empty_rows].index.tolist()
            result.add_warning(f"Found completely empty rows", empty_indices)
        
        result.add_info(f"Total rows: {len(df)}")
        result.add_info(f"Total columns: {len(df.columns)}")
    
    def _validate_columns(self, df: pd.DataFrame, result: ValidationResult):
        """Validate column names and presence."""
        strict_checking = self.config.get('data_validation.strict_column_checking', True)
        
        # Find column mappings
        found_columns = {}
        missing_columns = []
        
        for standard_name, variations in self.column_mappings.items():
            found = False
            for variation in variations:
                if variation in df.columns:
                    found_columns[standard_name] = variation
                    found = True
                    break
            
            if not found:
                missing_columns.append(standard_name)
        
        # Report missing columns
        if missing_columns:
            if strict_checking:
                result.add_error(f"Missing required columns: {', '.join(missing_columns)}")
            else:
                result.add_warning(f"Missing optional columns: {', '.join(missing_columns)}")
        
        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            result.add_error(f"Duplicate column names found: {', '.join(duplicate_cols)}")
        
        # Check for unusual column names (contains special characters)
        unusual_cols = [col for col in df.columns if not re.match(r'^[a-zA-Z0-9\s\(\)&_-]+$', str(col))]
        if unusual_cols:
            result.add_warning(f"Columns with unusual characters: {', '.join(unusual_cols)}")
        
        result.add_info(f"Column mapping: {found_columns}")
    
    def _validate_data_types(self, df: pd.DataFrame, result: ValidationResult):
        """Validate data types and formats."""
        # Check for mixed data types in numeric-expected columns
        numeric_columns = ['latitude', 'longitude']
        
        for col_key in numeric_columns:
            if col_key in self.column_mappings:
                for variation in self.column_mappings[col_key]:
                    if variation in df.columns:
                        col = df[variation]
                        
                        # Check if column contains non-numeric values
                        non_numeric = pd.to_numeric(col, errors='coerce').isna() & col.notna()
                        if non_numeric.any():
                            indices = df[non_numeric].index.tolist()
                            result.add_warning(f"Non-numeric values in {variation}", indices)
                        break
        
        # Check date columns
        date_columns = ['modified_date']
        for col_key in date_columns:
            if col_key in self.column_mappings:
                for variation in self.column_mappings[col_key]:
                    if variation in df.columns:
                        col = df[variation]
                        
                        # Try to parse dates
                        try:
                            pd.to_datetime(col, errors='coerce')
                        except Exception:
                            result.add_warning(f"Date parsing issues in {variation}")
                        break
    
    def _validate_content(self, df: pd.DataFrame, result: ValidationResult):
        """Validate content quality and consistency."""
        # Validate pole numbers
        self._validate_pole_numbers(df, result)
        
        # Validate coordinates
        self._validate_coordinates(df, result)
        
        # Validate email formats
        self._validate_email_formats(df, result)
        
        # Validate flow name groups
        self._validate_flow_groups(df, result)
    
    def _validate_pole_numbers(self, df: pd.DataFrame, result: ValidationResult):
        """Validate pole number format and content."""
        pole_col = None
        for variation in self.column_mappings['pole_number']:
            if variation in df.columns:
                pole_col = variation
                break
        
        if not pole_col:
            return
        
        pole_series = df[pole_col].astype(str)
        min_length = self.config.get('data_validation.min_pole_number_length', 1)
        
        # Check for empty/null pole numbers
        empty_poles = df[pole_col].isna() | (pole_series == '') | (pole_series == 'nan')
        if empty_poles.any():
            indices = df[empty_poles].index.tolist()
            result.add_error(f"Empty pole numbers found", indices)
        
        # Check pole number length
        short_poles = (pole_series.str.len() < min_length) & ~empty_poles
        if short_poles.any():
            indices = df[short_poles].index.tolist()
            result.add_warning(f"Pole numbers shorter than {min_length} characters", indices)
        
        # Check for duplicate pole numbers
        duplicates = pole_series.duplicated(keep=False) & ~empty_poles
        if duplicates.any():
            indices = df[duplicates].index.tolist()
            result.add_warning(f"Duplicate pole numbers found", indices)
        
        # Check for unusual characters in pole numbers
        unusual_pattern = re.compile(r'[^a-zA-Z0-9_-]')
        unusual_poles = pole_series.str.contains(unusual_pattern, na=False)
        if unusual_poles.any():
            indices = df[unusual_poles].index.tolist()
            result.add_info(f"Pole numbers with special characters", indices)
    
    def _validate_coordinates(self, df: pd.DataFrame, result: ValidationResult):
        """Validate latitude and longitude values."""
        allow_missing = self.config.get('data_validation.allow_missing_coordinates', False)
        
        lat_col = None
        lon_col = None
        
        for variation in self.column_mappings['latitude']:
            if variation in df.columns:
                lat_col = variation
                break
        
        for variation in self.column_mappings['longitude']:
            if variation in df.columns:
                lon_col = variation
                break
        
        if not lat_col or not lon_col:
            if not allow_missing:
                result.add_error("Latitude and/or longitude columns not found")
            return
        
        # Convert to numeric
        lat_numeric = pd.to_numeric(df[lat_col], errors='coerce')
        lon_numeric = pd.to_numeric(df[lon_col], errors='coerce')
        
        # Check for missing coordinates
        missing_lat = lat_numeric.isna()
        missing_lon = lon_numeric.isna()
        missing_coords = missing_lat | missing_lon
        
        if missing_coords.any():
            indices = df[missing_coords].index.tolist()
            if allow_missing:
                result.add_warning(f"Missing coordinate data", indices)
            else:
                result.add_error(f"Missing coordinate data", indices)
        
        # Validate coordinate ranges
        invalid_lat = (lat_numeric < -90) | (lat_numeric > 90)
        if invalid_lat.any():
            indices = df[invalid_lat].index.tolist()
            result.add_error(f"Invalid latitude values (must be between -90 and 90)", indices)
        
        invalid_lon = (lon_numeric < -180) | (lon_numeric > 180)
        if invalid_lon.any():
            indices = df[invalid_lon].index.tolist()
            result.add_error(f"Invalid longitude values (must be between -180 and 180)", indices)
        
        # Check for coordinates at (0,0) which might indicate missing data
        zero_coords = (lat_numeric == 0) & (lon_numeric == 0)
        if zero_coords.any():
            indices = df[zero_coords].index.tolist()
            result.add_warning(f"Coordinates at (0,0) - possible missing data", indices)
    
    def _validate_email_formats(self, df: pd.DataFrame, result: ValidationResult):
        """Validate email format in modified_by field."""
        if not self.config.get('data_validation.validate_agent_email_format', True):
            return
        
        email_col = None
        for variation in self.column_mappings['modified_by']:
            if variation in df.columns:
                email_col = variation
                break
        
        if not email_col:
            return
        
        email_series = df[email_col].astype(str)
        
        # Check for email format
        contains_at = email_series.str.contains('@', na=False)
        
        # Only validate non-empty entries that should be emails
        non_empty = (email_series != '') & (email_series != 'nan') & email_series.notna()
        should_be_email = non_empty & contains_at
        
        if should_be_email.any():
            # Validate email format
            valid_emails = email_series[should_be_email].apply(
                lambda x: bool(self.email_pattern.match(x))
            )
            
            invalid_emails = should_be_email & ~valid_emails
            if invalid_emails.any():
                indices = df[invalid_emails].index.tolist()
                result.add_warning(f"Invalid email formats in {email_col}", indices)
    
    def _validate_flow_groups(self, df: pd.DataFrame, result: ValidationResult):
        """Validate flow name groups content."""
        flow_col = None
        for variation in self.column_mappings['flow_name_groups']:
            if variation in df.columns:
                flow_col = variation
                break
        
        if not flow_col:
            return
        
        flow_series = df[flow_col].astype(str)
        
        # Check for pole permission entries
        has_pole_permission = flow_series.str.contains('Pole Permission', case=False, na=False)
        pole_permission_count = has_pole_permission.sum()
        
        result.add_info(f"Entries with 'Pole Permission': {pole_permission_count}")
        
        # Check for common flow types
        flow_types = {
            'Home Sign Ups': flow_series.str.contains('Home Sign Ups', case=False, na=False).sum(),
            'Pole Permission': pole_permission_count,
            'Service Installation': flow_series.str.contains('Service Installation', case=False, na=False).sum()
        }
        
        result.add_info(f"Flow type distribution: {flow_types}")
        
        # Check for empty flow groups
        empty_flows = flow_series.isna() | (flow_series == '') | (flow_series == 'nan')
        if empty_flows.any():
            indices = df[empty_flows].index.tolist()
            result.add_warning(f"Empty flow name groups", indices)
    
    def _validate_business_rules(self, df: pd.DataFrame, result: ValidationResult):
        """Validate business-specific rules."""
        # Rule 1: Pole permission entries should have pole numbers
        flow_col = None
        pole_col = None
        
        for variation in self.column_mappings['flow_name_groups']:
            if variation in df.columns:
                flow_col = variation
                break
        
        for variation in self.column_mappings['pole_number']:
            if variation in df.columns:
                pole_col = variation
                break
        
        if flow_col and pole_col:
            flow_series = df[flow_col].astype(str)
            pole_series = df[pole_col].astype(str)
            
            # Find pole permission entries without pole numbers
            has_pole_permission = flow_series.str.contains('Pole Permission', case=False, na=False)
            empty_poles = pole_series.isna() | (pole_series == '') | (pole_series == 'nan')
            
            pole_perm_no_pole = has_pole_permission & empty_poles
            if pole_perm_no_pole.any():
                indices = df[pole_perm_no_pole].index.tolist()
                result.add_error(f"Pole permission entries without pole numbers", indices)
        
        # Rule 2: Check for reasonable date ranges
        date_col = None
        for variation in self.column_mappings['modified_date']:
            if variation in df.columns:
                date_col = variation
                break
        
        if date_col:
            try:
                dates = pd.to_datetime(df[date_col], errors='coerce')
                current_date = datetime.now()
                
                # Check for future dates
                future_dates = dates > current_date
                if future_dates.any():
                    indices = df[future_dates].index.tolist()
                    result.add_warning(f"Future modification dates found", indices)
                
                # Check for very old dates (more than 10 years ago)
                very_old = dates < (current_date - pd.Timedelta(days=3650))
                if very_old.any():
                    indices = df[very_old].index.tolist()
                    result.add_info(f"Very old modification dates (>10 years)", indices)
                    
            except Exception:
                result.add_warning(f"Could not validate date ranges in {date_col}")
    
    def _generate_statistics(self, df: pd.DataFrame, result: ValidationResult):
        """Generate validation statistics."""
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_data_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'duplicate_rows': df.duplicated().sum(),
            'unique_values_per_column': {col: df[col].nunique() for col in df.columns[:10]}  # Limit for performance
        }
        
        result.stats = stats
        result.add_info(f"Missing data: {stats['missing_data_percentage']:.2f}%")
        result.add_info(f"Duplicate rows: {stats['duplicate_rows']}")

def validate_data(df: pd.DataFrame, config=None) -> ValidationResult:
    """Convenience function to validate a dataframe."""
    validator = EnhancedDataValidator(config)
    return validator.validate_dataframe(df) 