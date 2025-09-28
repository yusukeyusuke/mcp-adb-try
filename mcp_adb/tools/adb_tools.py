"""
ADB Tools definitions for MCP

Contains tool schemas and descriptions for various ADB operations.
"""

from typing import Dict, Any, List

# Tool definitions that would be used with MCP
ADB_TOOLS = [
    {
        "name": "list_devices",
        "description": "List all connected Android devices",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_device_info", 
        "description": "Get detailed information about a specific device",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional, uses first available if not specified)"
                }
            },
            "required": []
        }
    },
    {
        "name": "shell_command",
        "description": "Execute a shell command on an Android device",
        "input_schema": {
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
    },
    {
        "name": "install_app",
        "description": "Install an APK file on an Android device",
        "input_schema": {
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
    },
    {
        "name": "uninstall_app",
        "description": "Uninstall an app by package name",
        "input_schema": {
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "Package name to uninstall"
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            },
            "required": ["package_name"]
        }
    },
    {
        "name": "push_file",
        "description": "Push a file from local system to Android device",
        "input_schema": {
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
    },
    {
        "name": "pull_file",
        "description": "Pull a file from Android device to local system", 
        "input_schema": {
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
    }
]


def get_tool_by_name(name: str) -> Dict[str, Any]:
    """Get tool definition by name"""
    for tool in ADB_TOOLS:
        if tool["name"] == name:
            return tool
    raise ValueError(f"Tool not found: {name}")


def get_all_tool_names() -> List[str]:
    """Get list of all available tool names"""
    return [tool["name"] for tool in ADB_TOOLS]