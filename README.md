# VeloVerify Advanced - Universal Data Processing System

A powerful, web-based data processing and analysis system designed for pole permissions and home sign-ups management.

## 🚀 Features

### Core Functionality
- **📁 Drag & Drop File Upload**: Easy CSV file processing with visual feedback
- **🔍 Advanced Filtering**: Multiple preset filters for different data types
- **📊 Real-time Analysis**: Instant data processing and visualization
- **📈 Multiple Export Formats**: CSV, Excel, JSON, and Visual HTML reports
- **🎯 Duplicate Management**: Smart duplicate detection with earliest date preference
- **📅 Date Range Analysis**: Comprehensive date range and active days tracking

### Filter Presets
- **Pole Permissions (All)**: Shows all pole permission records
- **Pole Permissions: Approved**: Only approved pole permissions
- **Pole Permissions: Declined**: Only declined pole permissions  
- **Home Sign Ups (All)**: Shows all home sign up records
- **Home Sign Ups: Approved**: Only approved home sign ups
- **Home Sign Ups: Declined**: Only declined home sign ups
- **Custom Filter**: Create your own filtering criteria

### Export Options
1. **📋 Clean Data CSV**: Just the filtered data rows
2. **📊 Summary CSV**: Comprehensive analysis and statistics
3. **📄 Excel Report**: Multi-sheet Excel with summary
4. **🔧 JSON Report**: Technical data export  
5. **📊 Visual HTML Report**: Beautiful visual analysis report

## 🎯 Quick Start

1. **Open the Application**: Open `veloverify_advanced.html` in any modern web browser
2. **Upload Your Data**: Drag and drop your CSV file onto the upload area
3. **Select Filter**: Choose the appropriate filter preset for your data type
4. **Configure Settings**: Adjust time grouping and analysis options as needed
5. **Process Data**: Click "Process Data" to analyze your file
6. **Download Reports**: Choose from multiple export formats

## 📊 Required Data Columns

The system expects CSV files with these specific columns:

### Core Columns (Required for All)
- `Property ID`
- `1map NAD ID` 
- `Pole Number`
- `Drop Number`
- `Stand Number`
- `Status`
- `Flow Name Groups`
- `Site`
- `Sections`
- `PONs`
- `Location Address`
- `Latitude`
- `Longitude`
- `Latitude & Longitude`

### Pole Permissions Columns (Red Columns)
- `Field Agent Name (pole permission)`
- `Last Modified Pole Permissions By`
- `Last Modified Pole Permissions Date`

### Home Sign Ups Columns (Yellow Columns)  
- `Field Agent Name (Home Sign Ups)`
- `Last Modified Home Sign Ups By`
- `Last Modified Home Sign Ups Date`

### Legacy Columns (Supported)
- `lst_mod_by`
- `lst_mod_dt`

## 🔧 Configuration Options

### Filtering Settings
- **Filter Preset**: Choose from predefined filter types
- **Status Filter**: Include specific status values
- **Exclude Filter**: Exclude specific status values
- **Case Sensitive**: Toggle case-sensitive filtering
- **UID Field**: Unique identifier field (auto-set by preset)

### Analysis Settings
- **Time Grouping**: All Time, Last 30 Days, Last 7 Days, or Custom Range
- **Include Summary**: Generate summary statistics
- **Include Quality Control**: Add data quality analysis

### Validation Settings
- **Quality Level**: Standard or strict validation
- **Validate Agents**: Check agent name consistency
- **Coordinate Validation**: Validate latitude/longitude format
- **Duplicate Method**: Always use earliest date for first status achievement

## 📈 Data Processing Logic

### Duplicate Handling
- Uses the selected UID field (Pole Number or Drop Number) to identify duplicates
- **Always keeps the earliest date** for first status achievement
- Maintains data integrity across different date formats

### Column-Specific Display
- **Pole Permissions**: Shows Pole Number, excludes Drop Number and Home Sign Up columns
- **Home Sign Ups**: Shows Drop Number, excludes Pole Number and Pole Permission columns  
- **Filter-appropriate fields**: Only displays relevant agent and date columns

### Date Range Analysis
- Automatically detects actual data date range from multiple date fields
- Counts active days with data vs total span
- Supports multiple date formats for maximum compatibility

## 📊 Report Outputs

### Visual HTML Report
Professional, responsive reports with:
- Executive summary with key metrics
- Daily breakdown with peak day highlighting
- Agent performance analysis with rankings  
- Data quality assessment
- Key insights and operational patterns

### Summary CSV Report
Structured CSV with sections for:
- Processing statistics and metadata
- Date range analysis with active days
- Agent performance metrics
- Top 10 agents table
- Daily breakdown analysis
- Data quality indicators

### Clean Data CSV
- Just the filtered data rows
- Preset-appropriate columns only
- Clean format for further analysis or import

## 🎨 User Interface

### Modern Design
- **Responsive layout** that works on desktop and mobile
- **Drag & drop interface** with visual feedback
- **Real-time progress indicators** during processing
- **Professional styling** with gradients and animations

### Configuration Management
- **Tabbed interface** for different setting categories
- **Preset management** with automatic field locking
- **Visual filter criteria display** showing current settings
- **Smart validation** with helpful error messages

## 🔍 Quality Control Features

### Data Validation
- **Column presence checking** for all required fields
- **Agent name consistency** analysis across records
- **Email format validation** for all email fields
- **Coordinate format checking** for latitude/longitude

### Quality Reporting
- **Multiple email detection** for agents
- **Data completeness analysis** 
- **Processing statistics** with before/after counts
- **Traceability verification** ensuring all records are accountable

## 📁 File Structure

```
VeloVerify/
├── veloverify_advanced.html    # Main application (self-contained)
├── README.md                   # This documentation
├── requirements.txt            # Python dependencies (legacy)
└── [other legacy files]        # Previous system versions
```

## 🌟 Key Advantages

- **Self-Contained**: Single HTML file with no external dependencies
- **Universal Compatibility**: Works in any modern web browser
- **No Installation Required**: Just open and use
- **Professional Output**: Enterprise-ready reports and analysis
- **Flexible Filtering**: Handles multiple data types and scenarios
- **Data Integrity**: Smart duplicate handling and validation
- **Export Variety**: Multiple formats for different use cases

## 🔧 Technical Details

- **Frontend**: Pure HTML5, CSS3, and vanilla JavaScript
- **No Server Required**: Runs entirely in the browser
- **File Processing**: Client-side CSV parsing and analysis
- **Export Generation**: Dynamic file creation and download
- **Responsive Design**: CSS Grid and Flexbox for modern layouts

## 📋 Usage Examples

### Pole Permissions Analysis
1. Select "Pole Permissions: Approved" filter
2. Upload CSV with pole permission data
3. System automatically uses Pole Number as UID
4. Displays only pole permission relevant columns
5. Generate reports showing approval trends and agent performance

### Home Sign Ups Tracking  
1. Select "Home Sign Ups: Approved" filter
2. Upload CSV with home sign up data
3. System automatically uses Drop Number as UID
4. Displays only home sign up relevant columns
5. Analyze sign up patterns and agent effectiveness

## 🛠️ Development

The system is built as a single-file application for maximum portability and ease of deployment. All functionality is contained within `veloverify_advanced.html`.

## 📄 License

[License information to be added]

## 🤝 Contributing

[Contributing guidelines to be added]

---

**VeloVerify Advanced** - Transforming data processing with intelligent analysis and beautiful reporting. 