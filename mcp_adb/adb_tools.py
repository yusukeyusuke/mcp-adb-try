"""
ADB Tools - Wrapper for Android Debug Bridge operations

This module provides Python wrappers for ADB commands to interact with
Android devices.
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, List, Optional, Union


class ADBError(Exception):
    """Custom exception for ADB operations"""
    pass


class ADBTools:
    """Wrapper class for ADB operations"""
    
    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.logger = logging.getLogger(__name__)
        
    async def _run_command(self, args: List[str]) -> str:
        """Execute an ADB command asynchronously"""
        cmd = [self.adb_path] + args
        self.logger.debug(f"Executing: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                raise ADBError(f"ADB command failed: {error_msg}")
                
            return stdout.decode().strip()
            
        except FileNotFoundError:
            raise ADBError(f"ADB executable not found at: {self.adb_path}")
        except Exception as e:
            raise ADBError(f"Failed to execute ADB command: {str(e)}")
    
    async def list_devices(self) -> List[Dict[str, str]]:
        """List connected Android devices"""
        output = await self._run_command(["devices", "-l"])
        devices = []
        
        for line in output.split('\n')[1:]:  # Skip header line
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]
                    
                    device_info = {
                        "id": device_id,
                        "status": status
                    }
                    
                    # Parse additional device properties
                    for part in parts[2:]:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            device_info[key] = value
                    
                    devices.append(device_info)
        
        return devices
    
    async def get_device_info(self, device_id: Optional[str] = None) -> Dict[str, str]:
        """Get detailed information about a device"""
        cmd_args = []
        if device_id:
            cmd_args.extend(["-s", device_id])
        cmd_args.extend(["shell", "getprop"])
        
        output = await self._run_command(cmd_args)
        props = {}
        
        for line in output.split('\n'):
            if ': [' in line:
                # Parse property format: [key]: [value]
                parts = line.split(': [', 1)
                if len(parts) == 2:
                    key = parts[0].strip('[]')
                    value = parts[1].rstrip(']')
                    props[key] = value
        
        return props
    
    # TODO: Add more ADB operations
    # - install_app
    # - uninstall_app  
    # - push_file
    # - pull_file
    # - shell_command
    # - screenshot
    # - start_app
    # - stop_app
    # - get_logcat


# Example usage for testing
async def main():
    """Test function for ADB tools"""
    adb = ADBTools()
    
    try:
        devices = await adb.list_devices()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device}")
            
        if devices and devices[0]["status"] == "device":
            info = await adb.get_device_info(devices[0]["id"])
            print(f"Device info sample: {dict(list(info.items())[:5])}")
            
    except ADBError as e:
        print(f"ADB Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())