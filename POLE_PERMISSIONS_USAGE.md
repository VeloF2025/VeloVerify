# VeloVerify Advanced - Pole Permissions Processing Guide

## Quick Start

VeloVerify Advanced is now configured to process pole permissions data using exactly **17 required columns** in the specified order. The system automatically filters out any extra columns and validates that all required columns are present.

## Required Columns (Exact Names)

Your CSV file **must** contain these exact column names:

```
1.  Property ID
2.  1map NAD ID
3.  Pole Number
4.  Drop Number
5.  Stand Number
6.  Status
7.  Flow Name Groups
8.  Site
9.  Sections
10. PONs
11. Location Address
12. Latitude
13. Longitude
14. Field Agent Name (pole permission)
15. Latitude & Longitude
16. lst_mod_by
17. lst_mod_dt
```

## How to Use

### 1. Open VeloVerify Advanced
- Open `veloverify_advanced.html` in your web browser
- Or navigate to: `file:///C:/Jarvis/VeloVerify/veloverify_advanced.html`

### 2. Configure Processing Settings

**Filtering Tab:**
- **Select Filter Type**: Choose from predefined filters or create custom
  - **Pole Permissions**: Filters **Status** column for "Pole Permission: Approved", excludes "Home Sign Ups", UID: **Pole Number**
  - **Home Sign Ups**: Filters **Status** column for "Home Sign Ups", excludes "Pole Permission", UID: **Drop Number**
  - **Custom Filter**: Define your own include/exclude criteria, choose UID manually
- **Unique Identifier**: Automatically set based on filter type (locked for presets, customizable for custom)
- **Column Display**: Pole Permissions hides Drop Number, Home Sign Ups hides Pole Number in display
- ✅ **Handle Complex Flow Groups**: Enabled for concatenated status handling
- **Case Sensitive**: Usually disabled

**Validation Tab:**
- **Quality Control Level**: `Standard` (recommended)
- ✅ **Agent Email Validation**: Validates `lst_mod_by` email format
- ✅ **Coordinate Validation**: Validates latitude/longitude ranges
- **Duplicate Method**: `Keep Earliest Date` (default)

**Analysis Tab:**
- **Time Grouping**: `Weekly Breakdown` (default) - Creates sheets for weeks ending Sunday
- ✅ **Include Summary Sheet**: Processing statistics and insights
- ✅ **Include QC Sheets**: Quality control findings
- 🟢 **View All Filtered Records**: Quick access button to view all records matching current filter sorted newest first

### 3. Upload and Process Data

1. **Drag & drop** your CSV file into the upload area, or **click to browse**
2. System validates that all 17 required columns are present
3. Click **"Process Data"** button
4. Monitor progress bar for processing status

### 4. Review Results

**Statistics Overview:**
- Total entries processed
- Unique poles identified  
- Duplicates removed
- Data quality metrics

**Business Insights:**
- Peak activity periods
- Duplicate patterns
- Quality control findings

**Result Sheets:**
- Weekly breakdown sheets (e.g., "Week Ending 2025-06-08")
- Quality control sheets (duplicates, missing data, validation errors)
- Summary statistics

### 5. View All Filtered Records (Enhanced Feature)

**Quick Access Button:**
- Click **"View All Filtered Records"** in the Analysis tab
- Shows all records matching current filter preset sorted by date (newest first)
- Dynamically updates based on selected filter (Pole Permissions, Home Sign Ups, or Custom)
- Full-screen modal with all 17 columns
- Direct CSV download available
- Close with Escape key or click outside modal

### 6. Download Results

Available formats:
- **Excel Report**: Complete multi-sheet Excel file
- **Individual CSV**: Each analysis sheet as separate CSV
- **JSON Report**: Complete dataset with metadata
- **All Approved CSV**: Direct download of all approved permissions (newest first)

## Processing Logic

### Step 1: Data Filtering
- **Filters Status Column**: Looks at `Status` column (not Flow Name Groups)
- **Pole Permissions**: Includes records where Status contains "Pole Permission: Approved"
- **Home Sign Ups**: Includes records where Status contains "Home Sign Ups"
- Excludes records with exclude filter unless they also have target status

### Step 2: Quality Control
- **Missing Pole Numbers**: Moved to "No_Pole_Allocated" sheet
- **Agent Validation**: Checks email format in `lst_mod_by`
- **Date Validation**: Handles mixed ISO/JavaScript date formats
- **Coordinate Validation**: Validates lat/long ranges

### Step 3: Duplicate Removal
- Groups by selected **Unique Identifier** (`Pole Number` or `Drop Number`)
- **Always keeps earliest** `lst_mod_dt` for each UID (first status achievement)
- Moves duplicates to "Duplicate_Poles_Removed" sheet with detailed reason
- Consistent duplicate handling regardless of filter type

### Step 4: Time Analysis
- **Weekly**: Groups by weeks ending Sunday
- **Monthly**: Groups by calendar month
- **Complete**: All data in single sheet
- **Custom**: User-defined date range

## Expected Results

Based on your prompt example:
- **Total Entries**: ~5,287
- **Unique Poles**: ~3,732  
- **Duplicates Removed**: ~1,555
- **Peak Week**: Week ending 2025-06-08 with ~1,237 approvals

## New Features (Latest Update)

### 🎯 **Filter Preset System**
- **Predefined Filters**: Quick selection between different processing types
  - **Pole Permissions**: Filters Status for "Pole Permission: Approved", UID: **Pole Number**, displays relevant pole columns
  - **Home Sign Ups**: Filters Status for "Home Sign Ups", UID: **Drop Number**, displays relevant drop columns  
  - **Custom Filter**: Create your own include/exclude criteria and choose UID manually
- **Column-Specific Display**: Each preset shows only relevant columns (no Drop Number for Pole Permissions, etc.)
- **Status Column Filtering**: All filtering happens on Status column, not Flow Name Groups
- **Automatic UID Selection**: Each preset automatically sets the correct unique identifier
- **Smart Lock Protection**: Predefined presets lock UID field to prevent contradictions

### 📅 **Newest-to-Oldest Sorting**
- All result tabs now display in chronological order (newest first)
- Weekly sheets: Most recent week appears first
- Monthly sheets: Current/latest month appears first
- Data within each sheet: Sorted by date (newest entries first)

### 👁️ **Enhanced View All Records**
- Instant access to all records matching current filter
- Dynamically updates based on selected filter preset
- Real-time filtering from original data
- Full-screen modal with scrollable table
- Direct CSV download with timestamp
- Keyboard shortcuts (Escape to close)

## Column-Specific Processing

### Key Columns:
- **`Status`**: Primary filtering column (contains "Pole Permission: Approved", "Home Sign Ups", etc.)
- **`Pole Number`**: Primary identifier for Pole Permissions deduplication
- **`Drop Number`**: Primary identifier for Home Sign Ups deduplication
- **`lst_mod_dt`**: Date field for chronological analysis and duplicate resolution
- **`lst_mod_by`**: Agent email validation
- **`Field Agent Name (pole permission)`**: Cross-referenced with email
- **`Flow Name Groups`**: Contains detailed workflow information (not used for filtering)

### Validation Rules:
- **Property ID, 1map NAD ID**: Must be present
- **Coordinates**: Must be valid lat/long ranges if validation enabled
- **Dates**: Flexible parsing of ISO and JavaScript formats
- **Agent Data**: Email format validation for `lst_mod_by`

## Troubleshooting

**Missing Columns Error:**
- Ensure your CSV has exactly the 17 required column names
- Column names are case-sensitive and must match exactly

**No Data After Filtering:**
- Check that `Flow Name Groups` contains your target status
- Verify filter settings in Filtering tab

**Date Parsing Errors:**
- Check `lst_mod_dt` format - supports ISO and JavaScript dates
- Review Date Parse Errors sheet for specific issues

**Large File Processing:**
- Files >100MB will show progress indicators
- Processing may take several minutes for large datasets

## Working with Different Filters

### **Quick Filter Selection:**
1. **Pole Permissions** (Default): 
   - **Filters Status column** for "Pole Permission: Approved"
   - Excludes "Home Sign Ups" from Status
   - **Automatically uses Pole Number** as unique identifier
   - **Displays**: All columns except Drop Number (not needed for pole permissions)

2. **Home Sign Ups**: 
   - **Filters Status column** for "Home Sign Ups"
   - Excludes "Pole Permission" from Status  
   - **Automatically uses Drop Number** as unique identifier
   - **Displays**: All columns including Drop Number (essential for home sign ups)

3. **Custom Filter**: 
   - Define your own Status column include/exclude criteria
   - Examples: "Installation: Completed", "Home Installation: Installed"
   - **Manual UID selection** between Pole Number or Drop Number
   - **Displays**: All 17 required columns

### **Switching Between Filters:**
1. Select desired filter from dropdown in Filtering tab
2. **Visual display automatically updates** showing include/exclude criteria and UID
3. **UID field locks automatically** for predefined presets (unlocked for custom)
4. Click **"View All Filtered Records"** for immediate preview
5. Process data normally for full analysis and reports

### **Universal Design:**
- Same processing logic works for any filter type
- Consistent duplicate handling across all filters
- Time-based analysis applies to any status type
- All export formats available regardless of filter 