import logging
import asyncio
from homeassistant.components.bluetooth import (
    async_register_callback,
    async_handle_bluetooth_scan,
    BluetoothScanningMode,
    BluetoothChange,
)

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass, timeout=7, passive_scanning=False):
    """Discover nearby Bluetooth devices."""
    _LOGGER.info(f"🔍 Starting Bluetooth scan (Passive: {passive_scanning})...")

    discovered_devices = []

    def device_found(service_info, change: BluetoothChange):
        """Callback when a device is found."""
        
        device_name = (
            getattr(service_info, "name", None)
            or getattr(service_info.advertisement, "local_name", None)
            or "Unknown"
        )
        device = {
            "name": device_name,
            "mac": service_info.address,
            "rssi": getattr(service_info, "rssi", -100),
            "service_uuids": service_info.service_uuids or [],
        }
        _LOGGER.info(f"📡 Found Bluetooth device: {device}")
        if device not in discovered_devices:
            discovered_devices.append(device)

    try:
        _LOGGER.info("📡 Registering Bluetooth scan callback...")

        scan_mode = BluetoothScanningMode.PASSIVE if passive_scanning else BluetoothScanningMode.ACTIVE

        stop_scan = async_register_callback(
            hass,
            device_found,
            match_dict={},  # ✅ Ensures all devices are matched
            mode=scan_mode  # ✅ Dynamically switch scanning mode
        )

        _LOGGER.info(f"⏳ Waiting {timeout} seconds for scan results...")
        await asyncio.sleep(timeout)  # ✅ Wait for scan to complete

        _LOGGER.info("🛑 Stopping Bluetooth scan...")
        hass.loop.call_soon_threadsafe(stop_scan)  # ✅ Ensures stop_scan() runs safely

    except Exception as e:
        _LOGGER.error(f"🔥 Error during Bluetooth scan: {e}")

    if not discovered_devices:
        _LOGGER.warning("⚠️ No Bluetooth devices found.")

    return discovered_devices







### **🔹 Extract Advertisement Data Properly**
def extract_adv_data(adv_data):
    """Extract attributes from AdvertisementData safely."""
    if adv_data is None:
        return {
            "local_name": "Unknown",
            "manufacturer": "Unknown",
            "service_uuids": [],
            "service_data": {},
            "manufacturer_data": {},
            "rssi": -100,
            "tx_power": "Unknown",
        }

    return {
        "local_name": getattr(adv_data, "local_name", "Unknown"),
        "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
        "service_uuids": getattr(adv_data, "service_uuids", []),
        "service_data": _serialize_bytes(getattr(adv_data, "service_data", {})),
        "manufacturer_data": _serialize_bytes(getattr(adv_data, "manufacturer_data", {})),
        "rssi": getattr(adv_data, "rssi", -100),
        "tx_power": getattr(adv_data, "tx_power", "Unknown"),
    }


### **🔹 Extract BLE Device Data Properly**
def extract_ble_device(device):
    """Extract attributes from BLEDevice safely."""
    return {
        "name": getattr(device, "name", "Unknown"),
        "mac": getattr(device, "address", "Unknown"),
        "details": str(getattr(device, "details", {})),
        "id": getattr(device, "id", "Unknown"),
    }


### **🔹 Helper Function for Serializing Byte Data**
def _serialize_bytes(data):
    """Convert bytearray or bytes to JSON serializable format."""
    if isinstance(data, (bytes, bytearray)):
        return list(data)
    elif isinstance(data, dict):
        return {key: _serialize_bytes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_bytes(item) for item in data]
    return data


### **🔹 Simulated Bluetooth Pairing, Connecting, Disconnecting**
def pair_device(mac_address):
    """Simulate pairing with a Bluetooth device."""
    try:
        _LOGGER.debug(f"Simulated pairing with {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error pairing with {mac_address}: {e}")
        return False

def connect_device(mac_address):
    """Simulate connecting to a Bluetooth device."""
    try:
        _LOGGER.debug(f"Simulated connecting to {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error connecting to {mac_address}: {e}")
        return False

def disconnect_device(mac_address):
    """Simulate disconnecting from a Bluetooth device."""
    try:
        _LOGGER.debug(f"Simulated disconnecting from {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error disconnecting from {mac_address}: {e}")
        return False
