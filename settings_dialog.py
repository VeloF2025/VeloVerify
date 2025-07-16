"""
VeloVerify Settings Dialog
GUI interface for configuring application settings.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any
import os

from config import get_config

class SettingsDialog:
    """Settings dialog for VeloVerify configuration."""
    
    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        self.parent = parent
        self.config = get_config()
        self.dialog = None
        self.settings_vars = {}
        self.changes_made = False
        
    def show(self):
        """Show the settings dialog."""
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("VeloVerify Settings")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
        self.load_current_settings()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.changes_made
    
    def create_widgets(self):
        """Create all widgets for the settings dialog."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for different setting categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky='nsew', pady=(0, 10))
        
        # Create tabs
        self.create_ui_tab()
        self.create_processing_tab()
        self.create_export_tab()
        self.create_validation_tab()
        self.create_advanced_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        # Buttons
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_to_defaults).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.on_cancel).pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Apply", 
                  command=self.on_apply).pack(side=tk.RIGHT, padx=(0, 10))
        
        ttk.Button(button_frame, text="OK", 
                  command=self.on_ok).pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_ui_tab(self):
        """Create UI settings tab."""
        ui_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ui_frame, text="Interface")
        
        # Theme selection
        ttk.Label(ui_frame, text="Theme:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['ui.theme'] = tk.StringVar()
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.settings_vars['ui.theme'],
                                  values=['light', 'dark'], state='readonly', width=20)
        theme_combo.grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        # Font size
        ttk.Label(ui_frame, text="Font Size:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['ui.font_size'] = tk.IntVar()
        font_spin = ttk.Spinbox(ui_frame, textvariable=self.settings_vars['ui.font_size'],
                               from_=8, to=16, width=10)
        font_spin.grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # Window size
        ttk.Label(ui_frame, text="Default Window Size:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        size_frame = ttk.Frame(ui_frame)
        size_frame.grid(row=2, column=1, sticky='w', pady=(0, 5))
        
        self.settings_vars['ui.window_size.width'] = tk.IntVar()
        self.settings_vars['ui.window_size.height'] = tk.IntVar()
        
        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT)
        ttk.Spinbox(size_frame, textvariable=self.settings_vars['ui.window_size.width'],
                   from_=600, to=1600, width=8).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT)
        ttk.Spinbox(size_frame, textvariable=self.settings_vars['ui.window_size.height'],
                   from_=400, to=1200, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Checkboxes
        self.settings_vars['ui.remember_window_state'] = tk.BooleanVar()
        ttk.Checkbutton(ui_frame, text="Remember window position and size",
                       variable=self.settings_vars['ui.remember_window_state']).grid(
                       row=3, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.settings_vars['ui.show_progress_details'] = tk.BooleanVar()
        ttk.Checkbutton(ui_frame, text="Show detailed progress information",
                       variable=self.settings_vars['ui.show_progress_details']).grid(
                       row=4, column=0, columnspan=2, sticky='w', pady=(0, 5))
    
    def create_processing_tab(self):
        """Create processing settings tab."""
        proc_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(proc_frame, text="Processing")
        
        # Encoding detection
        ttk.Label(proc_frame, text="File Encoding:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['processing.encoding_detection'] = tk.StringVar()
        encoding_combo = ttk.Combobox(proc_frame, 
                                     textvariable=self.settings_vars['processing.encoding_detection'],
                                     values=['auto', 'utf-8', 'cp1252'], state='readonly', width=20)
        encoding_combo.grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        # Chunk size
        ttk.Label(proc_frame, text="Processing Chunk Size:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['processing.chunk_size'] = tk.IntVar()
        chunk_spin = ttk.Spinbox(proc_frame, textvariable=self.settings_vars['processing.chunk_size'],
                                from_=1000, to=50000, increment=1000, width=15)
        chunk_spin.grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # Date format preference
        ttk.Label(proc_frame, text="Date Format:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['processing.date_format_preference'] = tk.StringVar()
        date_combo = ttk.Combobox(proc_frame,
                                 textvariable=self.settings_vars['processing.date_format_preference'],
                                 values=['auto', 'US', 'EU', 'ISO'], state='readonly', width=20)
        date_combo.grid(row=2, column=1, sticky='w', pady=(0, 5))
        
        # Checkboxes
        self.settings_vars['processing.auto_open_results'] = tk.BooleanVar()
        ttk.Checkbutton(proc_frame, text="Automatically open results after processing",
                       variable=self.settings_vars['processing.auto_open_results']).grid(
                       row=3, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.settings_vars['processing.keep_processing_logs'] = tk.BooleanVar()
        ttk.Checkbutton(proc_frame, text="Keep processing logs",
                       variable=self.settings_vars['processing.keep_processing_logs']).grid(
                       row=4, column=0, columnspan=2, sticky='w', pady=(0, 5))
    
    def create_export_tab(self):
        """Create export settings tab."""
        export_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(export_frame, text="Export")
        
        # Export location
        ttk.Label(export_frame, text="Default Export Location:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['export.default_location'] = tk.StringVar()
        location_combo = ttk.Combobox(export_frame,
                                     textvariable=self.settings_vars['export.default_location'],
                                     values=['source_folder', 'desktop', 'documents', 'custom'],
                                     state='readonly', width=20)
        location_combo.grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        # Custom path
        ttk.Label(export_frame, text="Custom Export Path:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        path_frame = ttk.Frame(export_frame)
        path_frame.grid(row=1, column=1, sticky='ew', pady=(0, 5))
        
        self.settings_vars['export.custom_export_path'] = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.settings_vars['export.custom_export_path'])
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="Browse", width=8,
                  command=self.browse_export_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Filename format
        ttk.Label(export_frame, text="Filename Format:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['export.filename_format'] = tk.StringVar()
        ttk.Entry(export_frame, textvariable=self.settings_vars['export.filename_format'],
                 width=40).grid(row=2, column=1, sticky='w', pady=(0, 5))
        
        # Excel formatting
        ttk.Label(export_frame, text="Excel Formatting:").grid(row=3, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['export.excel_formatting'] = tk.StringVar()
        format_combo = ttk.Combobox(export_frame,
                                   textvariable=self.settings_vars['export.excel_formatting'],
                                   values=['basic', 'professional', 'minimal'],
                                   state='readonly', width=20)
        format_combo.grid(row=3, column=1, sticky='w', pady=(0, 5))
        
        # Checkboxes
        self.settings_vars['export.include_summary_sheet'] = tk.BooleanVar()
        ttk.Checkbutton(export_frame, text="Include processing summary sheet",
                       variable=self.settings_vars['export.include_summary_sheet']).grid(
                       row=4, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.settings_vars['export.include_qc_sheets'] = tk.BooleanVar()
        ttk.Checkbutton(export_frame, text="Include quality control sheets",
                       variable=self.settings_vars['export.include_qc_sheets']).grid(
                       row=5, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        self.settings_vars['export.create_backup_copies'] = tk.BooleanVar()
        ttk.Checkbutton(export_frame, text="Create backup copies of output files",
                       variable=self.settings_vars['export.create_backup_copies']).grid(
                       row=6, column=0, columnspan=2, sticky='w', pady=(0, 5))
    
    def create_validation_tab(self):
        """Create data validation settings tab."""
        val_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(val_frame, text="Validation")
        
        # Quality control level
        ttk.Label(val_frame, text="Quality Control Level:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['data_validation.quality_control_level'] = tk.StringVar()
        qc_combo = ttk.Combobox(val_frame,
                               textvariable=self.settings_vars['data_validation.quality_control_level'],
                               values=['minimal', 'standard', 'strict'],
                               state='readonly', width=20)
        qc_combo.grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        # Duplicate detection method
        ttk.Label(val_frame, text="Duplicate Detection:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['data_validation.duplicate_detection_method'] = tk.StringVar()
        dup_combo = ttk.Combobox(val_frame,
                                textvariable=self.settings_vars['data_validation.duplicate_detection_method'],
                                values=['earliest_date', 'latest_date', 'manual_review'],
                                state='readonly', width=20)
        dup_combo.grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # Min pole number length
        ttk.Label(val_frame, text="Min Pole Number Length:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['data_validation.min_pole_number_length'] = tk.IntVar()
        ttk.Spinbox(val_frame, textvariable=self.settings_vars['data_validation.min_pole_number_length'],
                   from_=1, to=10, width=10).grid(row=2, column=1, sticky='w', pady=(0, 5))
        
        # Checkboxes
        self.settings_vars['data_validation.strict_column_checking'] = tk.BooleanVar()
        ttk.Checkbutton(val_frame, text="Strict column name checking",
                       variable=self.settings_vars['data_validation.strict_column_checking']).grid(
                       row=3, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.settings_vars['data_validation.allow_missing_coordinates'] = tk.BooleanVar()
        ttk.Checkbutton(val_frame, text="Allow missing coordinate data",
                       variable=self.settings_vars['data_validation.allow_missing_coordinates']).grid(
                       row=4, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        self.settings_vars['data_validation.validate_agent_email_format'] = tk.BooleanVar()
        ttk.Checkbutton(val_frame, text="Validate agent email format",
                       variable=self.settings_vars['data_validation.validate_agent_email_format']).grid(
                       row=5, column=0, columnspan=2, sticky='w', pady=(0, 5))
    
    def create_advanced_tab(self):
        """Create advanced settings tab."""
        adv_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(adv_frame, text="Advanced")
        
        # Max worker threads
        ttk.Label(adv_frame, text="Max Worker Threads:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['advanced.max_worker_threads'] = tk.IntVar()
        ttk.Spinbox(adv_frame, textvariable=self.settings_vars['advanced.max_worker_threads'],
                   from_=1, to=16, width=10).grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        # Max log files
        ttk.Label(adv_frame, text="Max Log Files to Keep:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.settings_vars['processing.max_log_files'] = tk.IntVar()
        ttk.Spinbox(adv_frame, textvariable=self.settings_vars['processing.max_log_files'],
                   from_=1, to=50, width=10).grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # Checkboxes
        self.settings_vars['advanced.debug_mode'] = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Enable debug mode",
                       variable=self.settings_vars['advanced.debug_mode']).grid(
                       row=2, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.settings_vars['advanced.performance_logging'] = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Enable performance logging",
                       variable=self.settings_vars['advanced.performance_logging']).grid(
                       row=3, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        self.settings_vars['advanced.memory_optimization'] = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Enable memory optimization",
                       variable=self.settings_vars['advanced.memory_optimization']).grid(
                       row=4, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        self.settings_vars['advanced.parallel_processing'] = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Enable parallel processing",
                       variable=self.settings_vars['advanced.parallel_processing']).grid(
                       row=5, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        self.settings_vars['advanced.temp_file_cleanup'] = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Automatic temporary file cleanup",
                       variable=self.settings_vars['advanced.temp_file_cleanup']).grid(
                       row=6, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        self.settings_vars['advanced.enable_experimental_features'] = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Enable experimental features",
                       variable=self.settings_vars['advanced.enable_experimental_features']).grid(
                       row=7, column=0, columnspan=2, sticky='w', pady=(0, 5))
    
    def browse_export_path(self):
        """Browse for custom export path."""
        current_path = self.settings_vars['export.custom_export_path'].get()
        if not current_path:
            current_path = os.path.expanduser("~")
        
        path = filedialog.askdirectory(
            title="Select Export Directory",
            initialdir=current_path
        )
        
        if path:
            self.settings_vars['export.custom_export_path'].set(path)
    
    def load_current_settings(self):
        """Load current settings into the dialog."""
        for key, var in self.settings_vars.items():
            value = self.config.get(key)
            if value is not None:
                try:
                    var.set(value)
                except tk.TclError:
                    # Handle type mismatches
                    pass
    
    def apply_settings(self):
        """Apply current settings."""
        try:
            for key, var in self.settings_vars.items():
                value = var.get()
                self.config.set(key, value)
            
            # Save configuration
            if self.config.save_config():
                self.changes_made = True
                return True
            else:
                messagebox.showerror("Error", "Failed to save configuration.")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
            return False
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?"):
            self.config.reset_to_defaults()
            self.load_current_settings()
    
    def on_ok(self):
        """Handle OK button click."""
        if self.apply_settings():
            self.dialog.destroy()
    
    def on_apply(self):
        """Handle Apply button click."""
        self.apply_settings()
    
    def on_cancel(self):
        """Handle Cancel button click."""
        self.dialog.destroy()

def show_settings(parent=None):
    """Show the settings dialog."""
    dialog = SettingsDialog(parent)
    return dialog.show() 