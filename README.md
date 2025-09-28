# MCP ADB Try

Android Debug Bridge (ADB) operations via Model Context Protocol (MCP).

## Overview

This project implements an MCP server that allows AI/LLM systems to interact with Android devices through ADB commands. It provides a standardized interface for device management, app operations, file transfers, and system interactions.

## Features

- **Device Management**: List, connect, and manage Android devices
- **App Operations**: Install, uninstall, start, and stop applications
- **File Operations**: Push/pull files, directory listing, permission management
- **System Operations**: Execute shell commands, get device info, capture screenshots
- **Advanced Features**: Logcat monitoring, input simulation, screen recording

## Installation

```bash
# Clone the repository
git clone https://github.com/yusukeyusuke/mcp-adb-try.git
cd mcp-adb-try

# Install dependencies
pip install -r requirements.txt

# Install ADB (Android Platform Tools)
# On Ubuntu/Debian:
sudo apt-get install android-tools-adb
# On macOS:
brew install android-platform-tools
```

## Quick Start

1. Connect your Android device and enable USB debugging
2. Start the MCP server:
```bash
python -m mcp_adb.server
```
3. The server will be available for MCP clients to connect

## Project Structure

```
mcp-adb-try/
├── mcp_adb/                 # Main package
│   ├── __init__.py
│   ├── server.py           # MCP server implementation
│   ├── adb_tools.py        # ADB operations wrapper
│   ├── tools/              # MCP tool definitions
│   └── config/             # Configuration files
├── tests/                   # Test suite
├── examples/               # Usage examples
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 mcp_adb/
black mcp_adb/
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Requirements

- Python 3.8+
- Android Debug Bridge (ADB)
- Android device with USB debugging enabled
