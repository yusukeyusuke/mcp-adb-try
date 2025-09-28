"""
Basic usage example for MCP ADB Try

This example demonstrates how to use the ADB tools to interact with
Android devices.
"""

import asyncio
from mcp_adb.adb_tools import ADBTools, ADBError


async def main():
    """Basic usage example"""
    print("MCP ADB Try - Basic Usage Example")
    print("=" * 40)
    
    # Initialize ADB tools
    adb = ADBTools()
    
    try:
        # List connected devices
        print("1. Listing connected devices...")
        devices = await adb.list_devices()
        
        if not devices:
            print("   No devices found. Make sure:")
            print("   - Your Android device is connected via USB")
            print("   - USB debugging is enabled")
            print("   - ADB drivers are installed")
            return
        
        print(f"   Found {len(devices)} device(s):")
        for device in devices:
            print(f"   - Device ID: {device['id']}")
            print(f"     Status: {device['status']}")
            if 'product' in device:
                print(f"     Product: {device['product']}")
            if 'model' in device:
                print(f"     Model: {device['model']}")
        
        # Get device information for the first available device
        if devices and devices[0]['status'] == 'device':
            print(f"\n2. Getting device information for {devices[0]['id']}...")
            device_info = await adb.get_device_info(devices[0]['id'])
            
            # Display some key properties
            key_props = [
                'ro.build.version.release',  # Android version
                'ro.product.manufacturer',   # Manufacturer
                'ro.product.model',         # Model name
                'ro.build.display.id',      # Build ID
            ]
            
            print("   Key device properties:")
            for prop in key_props:
                if prop in device_info:
                    print(f"   - {prop}: {device_info[prop]}")
        
        print(f"\n✅ Example completed successfully!")
        
    except ADBError as e:
        print(f"❌ ADB Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())