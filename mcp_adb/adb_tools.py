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
    
    def __init__(self, adb_path: str = "adb", mock_mode: bool = False):
        self.adb_path = adb_path
        self.mock_mode = mock_mode
        self.logger = logging.getLogger(__name__)
        
        # Auto-detect mock mode if ADB is not available
        if not mock_mode:
            try:
                result = subprocess.run([adb_path, "version"], capture_output=True, check=True)
                self.logger.info("ADB found and working")
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                self.mock_mode = True
                self.logger.info(f"ADB not found ({e}), enabling mock mode")
                
    async def _run_command(self, args: List[str]) -> str:
        """Execute an ADB command asynchronously"""
        if self.mock_mode:
            return await self._run_mock_command(args)
            
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
    
    async def _run_mock_command(self, args: List[str]) -> str:
        """Mock ADB command execution for testing"""
        self.logger.debug(f"Mock executing: adb {' '.join(args)}")
        
        if args == ["devices", "-l"]:
            return """List of devices attached
mock_device_001	device usb:1-1 product:sdk_gphone64_x86_64 model:Android_SDK_built_for_x86_64 device:generic_x86_64
mock_device_002	device usb:1-2 product:pixel7 model:Pixel_7 device:pixel7"""
        
        elif args[0] == "shell" and args[1] == "getprop":
            return """[ro.build.version.release]: [14]
[ro.product.manufacturer]: [Google]
[ro.product.model]: [Android SDK built for x86_64]
[ro.build.display.id]: [UpsideDownCake]
[ro.hardware]: [ranchu]"""
        
        elif args[:2] == ["-s", "mock_device_001"] and args[2:] == ["shell", "getprop"]:
            return """[ro.build.version.release]: [14]
[ro.product.manufacturer]: [Google]
[ro.product.model]: [Android SDK built for x86_64]
[ro.build.display.id]: [UpsideDownCake]
[ro.hardware]: [ranchu]"""
        
        elif "shell" in args:
            cmd_part = " ".join(args[args.index("shell")+1:])
            return f"Mock command output for: {cmd_part}"
        
        elif "install" in args:
            return "Success"
        
        elif "uninstall" in args:
            return "Success"
            
        elif "push" in args or "pull" in args:
            return f"Transferred successfully"
        
        else:
            return f"Mock response for: {' '.join(args)}"
    
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
    
    async def shell_command(self, command: str, device_id: Optional[str] = None) -> str:
        """Execute a shell command on the device"""
        cmd_args = []
        if device_id:
            cmd_args.extend(["-s", device_id])
        cmd_args.extend(["shell", command])
        
        return await self._run_command(cmd_args)
    
    async def install_app(self, apk_path: str, device_id: Optional[str] = None) -> bool:
        """Install an APK file on the device"""
        cmd_args = []
        if device_id:
            cmd_args.extend(["-s", device_id])
        cmd_args.extend(["install", apk_path])
        
        try:
            await self._run_command(cmd_args)
            return True
        except ADBError:
            return False
    
    async def uninstall_app(self, package_name: str, device_id: Optional[str] = None) -> bool:
        """Uninstall an app by package name"""
        cmd_args = []
        if device_id:
            cmd_args.extend(["-s", device_id])
        cmd_args.extend(["uninstall", package_name])
        
        try:
            await self._run_command(cmd_args)
            return True
        except ADBError:
            return False
    
    async def push_file(self, local_path: str, remote_path: str, device_id: Optional[str] = None) -> bool:
        """Push a file to the device"""
        cmd_args = []
        if device_id:
            cmd_args.extend(["-s", device_id])
        cmd_args.extend(["push", local_path, remote_path])
        
        try:
            await self._run_command(cmd_args)
            return True
        except ADBError:
            return False
    
    async def pull_file(self, remote_path: str, local_path: str, device_id: Optional[str] = None) -> bool:
        """Pull a file from the device"""
        cmd_args = []
        if device_id:
            cmd_args.extend(["-s", device_id])
        cmd_args.extend(["pull", remote_path, local_path])
        
        try:
            await self._run_command(cmd_args)
            return True
        except ADBError:
            return False

    # TODO: Add more ADB operations
    # - start_app
    # - stop_app
    # - get_logcat
    # - screenshot


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