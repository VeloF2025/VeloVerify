"""
Test script for VeloVerify data processor
Creates sample data and tests the processing pipeline.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile

def create_sample_data():
    """Create sample CSV data for testing."""
    
    # Sample data based on requirements
    sample_data = []
    
    # Create sample pole permission entries
    for i in range(100):
        entry = {
            'Property ID': f'PROP_{i:04d}',
            '1map NAD ID': f'NAD_{i:04d}',
            'Pole Number': f'POLE_{i:04d}' if i % 10 != 0 else '',  # Some missing poles
            'Drop Number': f'DROP_{i:04d}',
            'Stand Number': f'STAND_{i:04d}',
            'Status': 'Active',
            'Flow Name Groups': 'Pole Permission: Approved' if i % 3 == 0 else 'Home Sign Ups: Approved',
            'Site': f'Site_{i % 5}',
            'Sections': f'Section_{i % 3}',
            'PONs': f'PON_{i % 10}',
            'Location Address': f'{i} Test Street, Test City',
            'Latitude': -26.2041 + (np.random.random() - 0.5) * 0.1,
            'Longitude': 28.0473 + (np.random.random() - 0.5) * 0.1,
            'Field Agent Name (pole permission)': f'Agent_{i % 5}' if i % 4 != 0 else '',
            'Latitude & Longitude': f'-26.{i:04d}, 28.{i:04d}',
            'lst_mod_by': f'user{i % 10}@example.com' if i % 3 == 0 else f'user{i % 10}',
            'lst_mod_dt': (datetime.now() - timedelta(days=np.random.randint(0, 60))).strftime('%Y-%m-%d %H:%M:%S.%f%z')
        }
        sample_data.append(entry)
    
    # Add some duplicates with different dates
    for i in range(10):
        duplicate_entry = sample_data[i].copy()
        duplicate_entry['lst_mod_dt'] = (datetime.now() - timedelta(days=np.random.randint(61, 120))).strftime('%Y-%m-%d %H:%M:%S.%f%z')
        sample_data.append(duplicate_entry)
    
    return pd.DataFrame(sample_data)

def test_data_processor():
    """Test the data processor with sample data."""
    print("=" * 60)
    print("VeloVerify Data Processor Test")
    print("=" * 60)
    
    try:
        # Import the processor
        from data_processor import DataProcessor
        
        # Create sample data
        print("Creating sample data...")
        df = create_sample_data()
        
        # Save to temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            df.to_csv(temp_file.name, index=False, encoding='cp1252')
            temp_csv_path = temp_file.name
        
        print(f"Sample data saved to: {temp_csv_path}")
        print(f"Total records: {len(df)}")
        
        # Initialize processor
        def progress_callback(step, percentage):
            print(f"Progress: {percentage:3d}% - {step}")
        
        processor = DataProcessor(progress_callback=progress_callback)
        
        # Process the data
        print("\nProcessing data...")
        results = processor.process_data(temp_csv_path)
        
        # Display results
        print("\n" + "=" * 40)
        print("PROCESSING RESULTS")
        print("=" * 40)
        
        weekly_sheets = 0
        total_records = 0
        
        for sheet_name, sheet_df in results.items():
            print(f"{sheet_name}: {len(sheet_df)} records")
            if sheet_name.startswith('Week_Ending_'):
                weekly_sheets += 1
                total_records += len(sheet_df)
        
        print(f"\nSummary:")
        print(f"  Weekly sheets: {weekly_sheets}")
        print(f"  Total weekly records: {total_records}")
        print(f"  Duplicates removed: {len(results.get('Duplicate_Poles_Removed', []))}")
        print(f"  No pole allocated: {len(results.get('No_Pole_Allocated', []))}")
        
        # Test Excel export
        print("\nTesting Excel export...")
        from excel_exporter import ExcelExporter
        
        exporter = ExcelExporter(progress_callback=progress_callback)
        output_file = exporter.generate_filename()
        
        print(f"Creating Excel file: {output_file}")
        final_file = exporter.create_excel_file(results, output_file)
        
        # Validate export
        validation = exporter.validate_export(final_file)
        print(f"Excel file validation: {'✅ PASSED' if validation['is_valid'] else '❌ FAILED'}")
        print(f"File size: {validation['file_size'] / 1024:.2f} KB")
        print(f"Sheets created: {validation['sheet_count']}")
        
        # Cleanup
        os.unlink(temp_csv_path)
        
        print(f"\n✅ Test completed successfully!")
        print(f"Excel file created: {final_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_requirements():
    """Test if all required packages are installed."""
    print("Testing requirements...")
    
    required_packages = [
        'pandas',
        'openpyxl', 
        'chardet',
        'python-dateutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("\n✅ All required packages are installed!")
        return True

if __name__ == "__main__":
    print("VeloVerify Test Suite")
    print("=" * 60)
    
    # Test requirements first
    if test_requirements():
        print("\n")
        # Run data processor test
        test_data_processor()
    else:
        print("\n❌ Cannot run tests - missing required packages")
        print("Please install requirements with: pip install -r requirements.txt") 