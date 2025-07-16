"""
VeloVerify Configuration System
Handles application settings and user preferences.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Union
import logging

class VeloVerifyConfig:
    """Configuration manager for VeloVerify application."""
    
    def __init__(self, config_dir: Union[str, None] = None):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        
        # Set up config directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use user's home directory/.veloverify
            self.config_dir = Path.home() / '.veloverify'
        
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.default_config = {
            'ui': {
                'theme': 'light',  # 'light' or 'dark'
                'window_size': {'width': 900, 'height': 700},
                'window_position': 'center',
                'remember_window_state': True,
                'font_size': 10,
                'show_progress_details': True
            },
            'processing': {
                'default_output_format': 'excel',  # 'excel', 'csv', 'json'
                'auto_open_results': True,
                'keep_processing_logs': True,
                'max_log_files': 10,
                'chunk_size': 10000,  # For processing large files
                'encoding_detection': 'auto',  # 'auto', 'utf-8', 'cp1252'
                'date_format_preference': 'auto'  # 'auto', 'US', 'EU', 'ISO'
            },
            'data_validation': {
                'strict_column_checking': True,
                'allow_missing_coordinates': False,
                'min_pole_number_length': 1,
                'validate_agent_email_format': True,
                'duplicate_detection_method': 'earliest_date',  # 'earliest_date', 'latest_date', 'manual_review'
                'quality_control_level': 'standard'  # 'minimal', 'standard', 'strict'
            },
            'export': {
                'default_location': 'source_folder',  # 'source_folder', 'desktop', 'documents', 'custom'
                'custom_export_path': '',
                'filename_format': 'Lawley_Pole_Permissions_Weekly_{timestamp}',
                'include_summary_sheet': True,
                'include_qc_sheets': True,
                'excel_formatting': 'professional',  # 'basic', 'professional', 'minimal'
                'create_backup_copies': False
            },
            'advanced': {
                'debug_mode': False,
                'performance_logging': False,
                'memory_optimization': True,
                'parallel_processing': True,
                'max_worker_threads': 4,
                'temp_file_cleanup': True,
                'enable_experimental_features': False
            },
            'user_preferences': {
                'last_input_directory': '',
                'last_output_directory': '',
                'recently_processed_files': [],
                'max_recent_files': 10,
                'show_welcome_dialog': True,
                'auto_check_updates': True
            }
        }
        
        # Load existing configuration
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                config = self._merge_configs(self.default_config, loaded_config)
                self.logger.info("Configuration loaded successfully")
                return config
            else:
                self.logger.info("No configuration file found, using defaults")
                return self.default_config.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self.default_config.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'ui.theme')."""
        try:
            value = self.config
            for key in key_path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation."""
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the final key
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Set the final value
            config_ref[keys[-1]] = value
            return True
        except Exception as e:
            self.logger.error(f"Error setting config value {key_path}: {e}")
            return False
    
    def reset_to_defaults(self, section: Union[str, None] = None) -> bool:
        """Reset configuration to defaults."""
        try:
            if section:
                if section in self.default_config:
                    self.config[section] = self.default_config[section].copy()
                else:
                    self.logger.warning(f"Section '{section}' not found in defaults")
                    return False
            else:
                self.config = self.default_config.copy()
            
            self.logger.info(f"Configuration reset to defaults: {section or 'all sections'}")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
            return False
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults."""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self) -> Dict[str, list]:
        """Validate current configuration and return any issues."""
        issues = {
            'errors': [],
            'warnings': []
        }
        
        # Validate UI settings
        if self.get('ui.theme') not in ['light', 'dark']:
            issues['errors'].append("Invalid UI theme, must be 'light' or 'dark'")
        
        # Validate processing settings
        chunk_size = self.get('processing.chunk_size', 0)
        if not isinstance(chunk_size, int) or chunk_size < 1000:
            issues['warnings'].append("Chunk size should be at least 1000 for optimal performance")
        
        # Validate export settings
        export_location = self.get('export.default_location')
        if export_location == 'custom' and not self.get('export.custom_export_path'):
            issues['errors'].append("Custom export path must be specified when using custom location")
        
        # Validate paths
        custom_path = self.get('export.custom_export_path')
        if custom_path and not os.path.exists(custom_path):
            issues['warnings'].append(f"Custom export path does not exist: {custom_path}")
        
        return issues
    
    def get_export_path(self, source_file_path: Union[str, None] = None) -> str:
        """Get the export path based on configuration."""
        location = self.get('export.default_location', 'source_folder')
        
        if location == 'source_folder' and source_file_path:
            return os.path.dirname(source_file_path)
        elif location == 'desktop':
            return str(Path.home() / 'Desktop')
        elif location == 'documents':
            return str(Path.home() / 'Documents')
        elif location == 'custom':
            custom_path = self.get('export.custom_export_path')
            if custom_path and os.path.exists(custom_path):
                return custom_path
        
        # Fallback to desktop
        return str(Path.home() / 'Desktop')
    
    def add_recent_file(self, file_path: str):
        """Add a file to the recently processed files list."""
        recent_files = self.get('user_preferences.recently_processed_files', [])
        max_files = self.get('user_preferences.max_recent_files', 10)
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Trim to max length
        recent_files = recent_files[:max_files]
        
        self.set('user_preferences.recently_processed_files', recent_files)
    
    def get_recent_files(self) -> list:
        """Get list of recently processed files."""
        recent_files = self.get('user_preferences.recently_processed_files', [])
        # Filter out files that no longer exist
        existing_files = [f for f in recent_files if os.path.exists(f)]
        
        # Update the list if files were removed
        if len(existing_files) != len(recent_files):
            self.set('user_preferences.recently_processed_files', existing_files)
        
        return existing_files
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to a file for backup or sharing."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Configuration exported to: {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            self.config = self._merge_configs(self.default_config, imported_config)
            self.logger.info(f"Configuration imported from: {import_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False


# Global configuration instance
_config_instance = None

def get_config() -> VeloVerifyConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = VeloVerifyConfig()
    return _config_instance

def save_config() -> bool:
    """Save the global configuration."""
    return get_config().save_config() 