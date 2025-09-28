"""
Configuration Manager for MCP ADB Server

Handles loading and managing configuration settings from files and environment.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Configuration management for MCP ADB server"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to config directory relative to this file
            self.config_path = Path(__file__).parent / "config" / "default.json"
        
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Override with environment variables
            config = self._apply_env_overrides(config)
            return config
            
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "server": {
                "log_level": "INFO"
            },
            "adb": {
                "path": "adb",
                "timeout": 30,
                "retry_attempts": 3
            },
            "tools": {
                "enabled": [
                    "list_devices",
                    "get_device_info",
                    "shell_command",
                    "install_app",
                    "uninstall_app",
                    "push_file",
                    "pull_file"
                ]
            }
        }
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        # ADB path override
        adb_path = os.getenv('MCP_ADB_PATH')
        if adb_path:
            config['adb']['path'] = adb_path
        
        # Timeout override
        timeout = os.getenv('MCP_ADB_TIMEOUT')
        if timeout:
            try:
                config['adb']['timeout'] = int(timeout)
            except ValueError:
                pass
        
        # Log level override
        log_level = os.getenv('MCP_ADB_LOG_LEVEL')
        if log_level:
            config['server']['log_level'] = log_level.upper()
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._config = self._load_config()
    
    @property
    def adb_path(self) -> str:
        """Get ADB executable path"""
        return self.get('adb.path', 'adb')
    
    @property
    def adb_timeout(self) -> int:
        """Get ADB command timeout"""
        return self.get('adb.timeout', 30)
    
    @property
    def log_level(self) -> str:
        """Get logging level"""
        return self.get('server.log_level', 'INFO')
    
    @property
    def enabled_tools(self) -> list:
        """Get list of enabled tools"""
        return self.get('tools.enabled', [])