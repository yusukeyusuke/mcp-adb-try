"""
Test script for MCP ADB functionality
"""

import asyncio
from mcp_adb.adb_tools import ADBTools, ADBError


async def test_mock_mode():
    """Test ADB tools in mock mode"""
    print("Testing MCP ADB Tools in Mock Mode")
    print("=" * 40)
    
    # Force mock mode
    adb = ADBTools(mock_mode=True)
    
    try:
        # Test device listing
        print("1. Testing device listing...")
        devices = await adb.list_devices()
        print(f"   Found {len(devices)} mock devices:")
        for device in devices:
            print(f"   - ID: {device['id']}, Status: {device['status']}")
            if 'model' in device:
                print(f"     Model: {device['model']}")
        
        # Test device info
        if devices:
            print(f"\n2. Testing device info for {devices[0]['id']}...")
            info = await adb.get_device_info(devices[0]['id'])
            print("   Device properties:")
            for key, value in list(info.items())[:5]:  # First 5 properties
                print(f"   - {key}: {value}")
        
        # Test shell command
        print(f"\n3. Testing shell command...")
        output = await adb.shell_command("ls /")
        print(f"   Command output: {output}")
        
        # Test file operations
        print(f"\n4. Testing file operations...")
        push_result = await adb.push_file("/tmp/test.txt", "/data/test.txt")
        print(f"   Push file result: {push_result}")
        
        pull_result = await adb.pull_file("/data/test.txt", "/tmp/pulled.txt")
        print(f"   Pull file result: {pull_result}")
        
        print(f"\n✅ All tests completed successfully!")
        
    except ADBError as e:
        print(f"❌ ADB Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mock_mode())