"""
Basic tests for ADB Tools
"""

import pytest
from unittest.mock import AsyncMock, patch
from mcp_adb.adb_tools import ADBTools, ADBError


class TestADBTools:
    """Test cases for ADB Tools"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.adb = ADBTools()
    
    @pytest.mark.asyncio
    async def test_list_devices_success(self):
        """Test successful device listing"""
        mock_output = """List of devices attached
1234567890abcdef	device usb:1-1 product:test_product model:Test_Model device:test_device"""
        
        with patch.object(self.adb, '_run_command', return_value=mock_output) as mock_cmd:
            devices = await self.adb.list_devices()
            
            mock_cmd.assert_called_once_with(["devices", "-l"])
            assert len(devices) == 1
            assert devices[0]["id"] == "1234567890abcdef"
            assert devices[0]["status"] == "device"
    
    @pytest.mark.asyncio
    async def test_list_devices_empty(self):
        """Test device listing when no devices connected"""
        mock_output = "List of devices attached"
        
        with patch.object(self.adb, '_run_command', return_value=mock_output):
            devices = await self.adb.list_devices()
            assert len(devices) == 0
    
    @pytest.mark.asyncio
    async def test_adb_command_failure(self):
        """Test ADB command failure handling"""
        with patch.object(self.adb, '_run_command', side_effect=ADBError("Command failed")):
            with pytest.raises(ADBError):
                await self.adb.list_devices()


if __name__ == "__main__":
    pytest.main([__file__])