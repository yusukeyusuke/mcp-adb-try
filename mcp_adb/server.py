"""
MCP Server for Android ADB operations

This module implements the Model Context Protocol server that provides
ADB (Android Debug Bridge) functionality to AI/LLM clients.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        Tool,
        TextContent,
        INVALID_PARAMS,
        INTERNAL_ERROR
    )
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for development without MCP installed
    MCP_AVAILABLE = False
    Server = object
    stdio_server = None

from .adb_tools import ADBTools, ADBError
from .config_manager import ConfigManager


class MCPADBServer:
    """MCP Server for ADB operations"""
    
    def __init__(self, mock_mode: bool = False):
        self.adb_tools = ADBTools(mock_mode=mock_mode)
        self.logger = logging.getLogger(__name__)
        self.server = None
        
        if MCP_AVAILABLE:
            self.server = Server("mcp-adb-try")
            self._register_handlers()
        else:
            self.logger.warning("MCP library not available. Running in development mode.")
    
    def _register_handlers(self) -> None:
        """Register MCP handlers"""
        if not self.server:
            return
            
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available ADB tools"""
            return [
                Tool(
                    name="list_devices",
                    description="List all connected Android devices",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_device_info",
                    description="Get detailed information about a specific device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID (optional, uses first available if not specified)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="shell_command",
                    description="Execute a shell command on an Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string", 
                                "description": "Shell command to execute"
                            },
                            "device_id": {
                                "type": "string",
                                "description": "Device ID (optional)"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="install_app",
                    description="Install an APK file on an Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "apk_path": {
                                "type": "string",
                                "description": "Path to the APK file"
                            },
                            "device_id": {
                                "type": "string",
                                "description": "Device ID (optional)"
                            }
                        },
                        "required": ["apk_path"]
                    }
                ),
                Tool(
                    name="push_file",
                    description="Push a file from local system to Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "local_path": {
                                "type": "string",
                                "description": "Local file path"
                            },
                            "remote_path": {
                                "type": "string", 
                                "description": "Remote path on device"
                            },
                            "device_id": {
                                "type": "string",
                                "description": "Device ID (optional)"
                            }
                        },
                        "required": ["local_path", "remote_path"]
                    }
                ),
                Tool(
                    name="pull_file",
                    description="Pull a file from Android device to local system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "remote_path": {
                                "type": "string",
                                "description": "Remote file path on device"
                            },
                            "local_path": {
                                "type": "string",
                                "description": "Local destination path"
                            },
                            "device_id": {
                                "type": "string",
                                "description": "Device ID (optional)"
                            }
                        },
                        "required": ["remote_path", "local_path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "list_devices":
                    devices = await self.adb_tools.list_devices()
                    result = {
                        "devices": devices,
                        "count": len(devices)
                    }
                    
                elif name == "get_device_info":
                    device_id = arguments.get("device_id")
                    info = await self.adb_tools.get_device_info(device_id)
                    result = {"device_info": info}
                    
                elif name == "shell_command":
                    command = arguments["command"]
                    device_id = arguments.get("device_id")
                    output = await self.adb_tools.shell_command(command, device_id)
                    result = {"output": output}
                    
                elif name == "install_app":
                    apk_path = arguments["apk_path"]
                    device_id = arguments.get("device_id")
                    success = await self.adb_tools.install_app(apk_path, device_id)
                    result = {"success": success}
                    
                elif name == "push_file":
                    local_path = arguments["local_path"]
                    remote_path = arguments["remote_path"]
                    device_id = arguments.get("device_id")
                    success = await self.adb_tools.push_file(local_path, remote_path, device_id)
                    result = {"success": success}
                    
                elif name == "pull_file":
                    remote_path = arguments["remote_path"]
                    local_path = arguments["local_path"] 
                    device_id = arguments.get("device_id")
                    success = await self.adb_tools.pull_file(remote_path, local_path, device_id)
                    result = {"success": success}
                    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except ADBError as e:
                error_result = {"error": str(e), "type": "ADBError"}
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
            except Exception as e:
                self.logger.exception(f"Error handling tool call {name}")
                error_result = {"error": str(e), "type": "UnknownError"}
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def start_stdio(self) -> None:
        """Start the MCP server using stdio transport"""
        if not MCP_AVAILABLE:
            self.logger.error("Cannot start server: MCP library not available")
            return
            
        if not stdio_server:
            self.logger.error("stdio_server not available")
            return
            
        self.logger.info("Starting MCP ADB server via stdio")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="mcp-adb-try",
                    server_version="0.1.0"
                )
            )
    
    async def start_demo(self) -> None:
        """Start in demo mode for development/testing"""
        self.logger.info("Starting MCP ADB server in demo mode")
        
        # Demo implementation without actual MCP transport
        print("MCP ADB Server - Demo Mode")
        print("=" * 40)
        
        try:
            # Test ADB functionality
            devices = await self.adb_tools.list_devices()
            print(f"Found {len(devices)} devices:")
            for device in devices:
                print(f"  - {device}")
                
            if devices:
                device_id = devices[0]['id']
                info = await self.adb_tools.get_device_info(device_id)
                print(f"\nDevice info sample (first 3 properties):")
                for i, (key, value) in enumerate(info.items()):
                    if i >= 3:
                        break
                    print(f"  {key}: {value}")
                        
        except ADBError as e:
            print(f"ADB Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nDemo completed. In production, this would run as MCP server.")


def main():
    """Main entry point for the server"""
    import sys
    
    # Check for mock mode flag
    mock_mode = "--mock" in sys.argv
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = MCPADBServer(mock_mode=mock_mode)
    
    try:
        if MCP_AVAILABLE:
            # Run as actual MCP server
            asyncio.run(server.start_stdio())
        else:
            # Run in demo mode for development
            asyncio.run(server.start_demo())
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()