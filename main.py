"""
VeloVerify - Main Application
Professional desktop application for processing pole permissions data.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
import threading
import os
import sys
from pathlib import Path
import webbrowser
from datetime import datetime

# Import our custom modules
from data_processor import DataProcessor
from excel_exporter import ExcelExporter

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("Note: tkinterdnd2 not available. Drag & drop will use click-to-browse fallback.")

class VeloVerifyApp:
    """Main application class for VeloVerify."""
    
    def __init__(self):
        """Initialize the main application."""
        # Initialize root window with drag-drop support if available
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
            
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.create_widgets()
        self.setup_drag_drop()
        
        # Processing components
        self.processor = None
        self.exporter = None
        self.current_file = None
        self.processing_results = None
        
        # Theme support
        self.dark_mode = False
        
    def setup_window(self):
        """Configure the main window."""
        self.root.title("VeloVerify - Pole Permissions Processor v1.1.0")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Configure icon if available
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass  # Icon file not found, continue without it
    
    def setup_styles(self):
        """Configure custom styles for the application."""
        self.style = ttk.Style()
        
        # Configure modern theme
        self.style.theme_use('clam')
        
        # Define color schemes
        self.light_colors = {
            'primary': '#366092',
            'secondary': '#4A90B8',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff',
            'bg': '#ffffff',
            'fg': '#000000',
            'border': '#dee2e6'
        }
        
        self.dark_colors = {
            'primary': '#5a9fd4',
            'secondary': '#6ba3d0',
            'success': '#40b762',
            'warning': '#ffc720',
            'danger': '#e74c3c',
            'light': '#2c3e50',
            'dark': '#ecf0f1',
            'white': '#34495e',
            'bg': '#2c3e50',
            'fg': '#ecf0f1',
            'border': '#34495e'
        }
        
        # Start with light theme
        self.colors = self.light_colors.copy()
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme colors to styles."""
        # Configure styles
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 24, 'bold'),
                           foreground=self.colors['primary'],
                           background=self.colors['bg'])
        
        self.style.configure('Subtitle.TLabel',
                           font=('Segoe UI', 11),
                           foreground=self.colors['dark'],
                           background=self.colors['bg'])
        
        self.style.configure('Success.TLabel',
                           foreground=self.colors['success'],
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg'])
        
        self.style.configure('Error.TLabel',
                           foreground=self.colors['danger'],
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg'])
        
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 11, 'bold'))
        
        self.style.configure('Theme.TButton',
                           font=('Segoe UI', 9))
        
        # Configure main background
        self.root.configure(bg=self.colors['bg'])
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        self.colors = self.dark_colors.copy() if self.dark_mode else self.light_colors.copy()
        self.apply_theme()
        
        # Update the drop frame colors
        if hasattr(self, 'drop_frame'):
            self.drop_frame.configure(bg=self.colors['light'])
            # Update child widgets
            for child in self.drop_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=self.colors['light'], fg=self.colors['dark'])
        
        # Update results text area
        if hasattr(self, 'results_text'):
            self.results_text.configure(bg=self.colors['white'], fg=self.colors['fg'])
    
    def setup_variables(self):
        """Initialize tkinter variables."""
        self.status_var = tk.StringVar(value="Ready to process CSV files")
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_text_var = tk.StringVar(value="")
        self.file_info_var = tk.StringVar(value="No file selected")
        self.processing_var = tk.BooleanVar(value=False)
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Create top toolbar
        self.create_toolbar(main_frame)
        
        # Title section
        self.create_title_section(main_frame)
        
        # File upload section
        self.create_file_section(main_frame)
        
        # Processing section
        self.create_processing_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Create the top toolbar with theme toggle and help."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=0, column=0, sticky='we', pady=(0, 10))
        toolbar_frame.columnconfigure(0, weight=1)
        
        # Right side buttons
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(right_frame,
                                   text="🌙 Dark",
                                   style='Theme.TButton',
                                   command=self.toggle_theme,
                                   width=10)
        self.theme_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Help button
        help_btn = ttk.Button(right_frame,
                             text="? Help",
                             style='Theme.TButton',
                             command=self.show_help,
                             width=8)
        help_btn.grid(row=0, column=1)
    
    def show_help(self):
        """Show help dialog with usage instructions."""
        help_text = """VeloVerify - Pole Permissions Processor Help

USAGE:
1. Drag & drop a CSV file or click 'Browse Files' to select
2. Click 'Process Data' to start processing
3. View results and download the generated Excel file

FEATURES:
• Removes duplicate pole entries (keeps earliest)
• Groups data into weekly sheets (ending Sunday)
• Performs quality control checks
• Generates professional Excel reports

SUPPORTED FILES:
• CSV files with pole permission data
• Must contain required columns (see documentation)

TIPS:
• Use dark mode for better eye comfort
• Processing large files may take a few minutes
• Generated files are saved in the same folder as input

For technical support, refer to the README.md file."""
        
        messagebox.showinfo("VeloVerify Help", help_text)
    
    def create_title_section(self, parent):
        """Create the title and description section."""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=1, column=0, sticky='we', pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(title_frame, text="VeloVerify", style='Title.TLabel')
        title_label.grid(row=0, column=0)
        
        # Subtitle
        subtitle_label = ttk.Label(title_frame, 
                                 text="Professional Excel Processor for Lawley Pole Permissions",
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
    
    def create_file_section(self, parent):
        """Create the file upload section."""
        file_frame = ttk.LabelFrame(parent, text="File Upload", padding="15")
        file_frame.grid(row=2, column=0, sticky='we', pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        # Drag and drop area
        self.drop_frame = tk.Frame(file_frame, 
                                  height=140, 
                                  bg=self.colors['light'],
                                  relief='ridge',
                                  bd=2)
        self.drop_frame.grid(row=0, column=0, sticky='we', pady=(0, 10))
        self.drop_frame.grid_propagate(False)
        self.drop_frame.columnconfigure(0, weight=1)
        
        # Drop area content
        drop_icon = tk.Label(self.drop_frame, 
                           text="📁", 
                           font=('Segoe UI', 40),
                           bg=self.colors['light'],
                           fg=self.colors['primary'])
        drop_icon.grid(row=0, column=0, pady=(25, 5))
        
        drop_text_main = tk.Label(self.drop_frame,
                                text="Drag & Drop CSV File Here",
                                font=('Segoe UI', 14, 'bold'),
                                bg=self.colors['light'],
                                fg=self.colors['dark'])
        drop_text_main.grid(row=1, column=0, pady=(0, 2))
        
        drop_text_sub = tk.Label(self.drop_frame,
                               text="or click to browse files",
                               font=('Segoe UI', 10),
                               bg=self.colors['light'],
                               fg=self.colors['secondary'])
        drop_text_sub.grid(row=2, column=0, pady=(0, 15))
        
        # Browse button
        browse_btn = ttk.Button(file_frame, 
                              text="Browse Files",
                              command=self.browse_file)
        browse_btn.grid(row=1, column=0, pady=(0, 10))
        
        # File info with enhanced display
        file_info_frame = ttk.Frame(file_frame)
        file_info_frame.grid(row=2, column=0, sticky='we')
        file_info_frame.columnconfigure(1, weight=1)
        
        info_label = ttk.Label(file_info_frame, text="Selected File:", style='Subtitle.TLabel')
        info_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_info_label = ttk.Label(file_info_frame, 
                                       textvariable=self.file_info_var,
                                       style='Subtitle.TLabel')
        self.file_info_label.grid(row=0, column=1, sticky=tk.W)
    
    def create_processing_section(self, parent):
        """Create the processing controls section."""
        proc_frame = ttk.LabelFrame(parent, text="Processing", padding="15")
        proc_frame.grid(row=3, column=0, sticky='we', pady=(0, 15))
        proc_frame.columnconfigure(0, weight=1)
        
        # Process button
        self.process_btn = ttk.Button(proc_frame,
                                    text="Process Data",
                                    style='Primary.TButton',
                                    command=self.start_processing,
                                    state='disabled')
        self.process_btn.grid(row=0, column=0, pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(proc_frame,
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress text
        self.progress_label = ttk.Label(proc_frame,
                                      textvariable=self.progress_text_var,
                                      style='Subtitle.TLabel')
        self.progress_label.grid(row=2, column=0)
    
    def create_results_section(self, parent):
        """Create the results display section."""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="15")
        results_frame.grid(row=4, column=0, sticky='wens', pady=(0, 15))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text area with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame,
                                  height=8,
                                  font=('Consolas', 10),
                                  wrap=tk.WORD,
                                  state='disabled')
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        btn_frame = ttk.Frame(results_frame)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.open_file_btn = ttk.Button(btn_frame,
                                      text="Open Excel File",
                                      command=self.open_excel_file,
                                      state='disabled')
        self.open_file_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.open_folder_btn = ttk.Button(btn_frame,
                                        text="Open Folder",
                                        command=self.open_output_folder,
                                        state='disabled')
        self.open_folder_btn.grid(row=0, column=1)
    
    def create_status_bar(self, parent):
        """Create the status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, sticky='we')
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ttk.Label(status_frame,
                                    textvariable=self.status_var,
                                    style='Subtitle.TLabel')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version label
        version_label = ttk.Label(status_frame,
                                text="v1.0.0",
                                style='Subtitle.TLabel')
        version_label.grid(row=0, column=1, sticky=tk.E)
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        if HAS_DND:
            # Note: Full drag-drop would need TkinterDnD properly configured
            pass
        
        # Always bind click event to drop frame as fallback
        self.drop_frame.bind("<Button-1>", lambda e: self.browse_file())
        
        # Update theme button text based on current mode
        def update_theme_button():
            if self.dark_mode:
                self.theme_btn.config(text="☀️ Light")
            else:
                self.theme_btn.config(text="🌙 Dark")
    
    def browse_file(self):
        """Open file browser to select CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load and validate the selected file."""
        try:
            if not file_path or not os.path.exists(file_path):
                messagebox.showerror("File Error", "File not found or path is invalid.")
                return
                
            self.current_file = file_path
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Update file info
            size_mb = file_size / (1024 * 1024)
            self.file_info_var.set(f"{file_name} ({size_mb:.2f} MB)")
            
            # Enable process button
            self.process_btn.config(state='normal')
            
            # Update status
            self.status_var.set(f"File loaded: {file_name}")
            
            # Clear previous results
            self.clear_results()
            
        except Exception as e:
            messagebox.showerror("File Error", f"Error loading file: {str(e)}")
    
    def start_processing(self):
        """Start the data processing in a separate thread."""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select a CSV file first.")
            return
        
        # Disable UI during processing
        self.processing_var.set(True)
        self.process_btn.config(state='disabled')
        
        # Start processing thread
        processing_thread = threading.Thread(target=self.process_data)
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_data(self):
        """Process the data (runs in separate thread)."""
        try:
            # Initialize processor with progress callback
            self.processor = DataProcessor(progress_callback=self.update_progress)
            
            # Process the data
            self.processing_results = self.processor.process_data(self.current_file)
            
            # Export to Excel
            self.exporter = ExcelExporter(progress_callback=self.update_progress)
            output_path = self.exporter.generate_filename(os.path.dirname(self.current_file))
            
            self.output_file = self.exporter.create_excel_file(self.processing_results, output_path)
            
            # Validate the output
            validation = self.exporter.validate_export(self.output_file)
            
            # Update UI on main thread
            self.root.after(0, self.processing_complete, validation)
            
        except Exception as e:
            # Handle errors on main thread
            self.root.after(0, self.processing_error, str(e))
    
    def update_progress(self, step, percentage):
        """Update progress bar and text (thread-safe)."""
        def update_ui():
            self.progress_var.set(percentage)
            self.progress_text_var.set(step)
        
        self.root.after(0, update_ui)
    
    def processing_complete(self, validation):
        """Handle successful processing completion."""
        # Re-enable UI
        self.processing_var.set(False)
        self.process_btn.config(state='normal')
        
        # Update progress
        self.progress_var.set(100)
        self.progress_text_var.set("Processing complete!")
        
        # Display results
        self.display_results(validation)
        
        # Enable action buttons
        self.open_file_btn.config(state='normal')
        self.open_folder_btn.config(state='normal')
        
        # Update status
        self.status_var.set("Processing completed successfully")
        
        # Show completion message
        messagebox.showinfo("Success", 
                          f"Processing completed!\nExcel file saved: {os.path.basename(self.output_file)}")
    
    def processing_error(self, error_message):
        """Handle processing errors."""
        # Re-enable UI
        self.processing_var.set(False)
        self.process_btn.config(state='normal')
        
        # Reset progress
        self.progress_var.set(0)
        self.progress_text_var.set("Processing failed")
        
        # Update status
        self.status_var.set("Processing failed")
        
        # Show error message
        messagebox.showerror("Processing Error", f"Processing failed:\n{error_message}")
    
    def display_results(self, validation):
        """Display processing results in the text area."""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        if self.processing_results and validation['is_valid']:
            # Create results summary
            results_text = "PROCESSING RESULTS\n"
            results_text += "=" * 50 + "\n\n"
            
            # File info
            results_text += f"Input File: {os.path.basename(self.current_file)}\n"
            results_text += f"Output File: {os.path.basename(self.output_file)}\n"
            results_text += f"Processing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Statistics
            if 'Processing_Summary' in self.processing_results:
                summary_df = self.processing_results['Processing_Summary']
                results_text += "STATISTICS\n"
                results_text += "-" * 20 + "\n"
                for _, row in summary_df.iterrows():
                    results_text += f"{row['Metric']}: {row['Value']}\n"
                results_text += "\n"
            
            # Sheets created
            results_text += "SHEETS CREATED\n"
            results_text += "-" * 20 + "\n"
            weekly_sheets = 0
            for sheet_name, df in self.processing_results.items():
                if sheet_name.startswith('Week_Ending_'):
                    weekly_sheets += 1
                    results_text += f"{sheet_name}: {len(df)} entries\n"
            
            results_text += f"\nTotal Weekly Sheets: {weekly_sheets}\n"
            
            # Quality control sheets
            qc_sheets = ['Duplicate_Poles_Removed', 'No_Pole_Allocated', 'Agent_Data_Mismatches']
            results_text += "\nQUALITY CONTROL\n"
            results_text += "-" * 20 + "\n"
            for sheet in qc_sheets:
                if sheet in self.processing_results:
                    count = len(self.processing_results[sheet])
                    results_text += f"{sheet}: {count} entries\n"
            
            # Validation info
            results_text += f"\nFILE VALIDATION\n"
            results_text += "-" * 20 + "\n"
            results_text += f"File Size: {validation['file_size'] / 1024 / 1024:.2f} MB\n"
            results_text += f"Total Sheets: {validation['sheet_count']}\n"
            results_text += f"Status: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}\n"
            
        else:
            results_text = "No results to display."
        
        self.results_text.insert(1.0, results_text)
        self.results_text.config(state='disabled')
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        # Disable action buttons
        self.open_file_btn.config(state='disabled')
        self.open_folder_btn.config(state='disabled')
        
        # Reset progress
        self.progress_var.set(0)
        self.progress_text_var.set("")
    
    def open_excel_file(self):
        """Open the generated Excel file."""
        if hasattr(self, 'output_file') and os.path.exists(self.output_file):
            try:
                if sys.platform.startswith('win'):
                    os.startfile(self.output_file)
                elif sys.platform.startswith('darwin'):
                    os.system(f'open "{self.output_file}"')
                else:
                    os.system(f'xdg-open "{self.output_file}"')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
        else:
            messagebox.showwarning("File Not Found", "Output file not found.")
    
    def open_output_folder(self):
        """Open the folder containing the output file."""
        if hasattr(self, 'output_file'):
            folder = os.path.dirname(self.output_file)
            try:
                if sys.platform.startswith('win'):
                    os.startfile(folder)
                elif sys.platform.startswith('darwin'):
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {str(e)}")
    
    def run(self):
        """Start the application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

def main():
    """Main entry point."""
    try:
        app = VeloVerifyApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Application Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main() 