from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        # Get the Bluetooth scanner object
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner not available.")
            return []

        # Check for discovered devices and advertisement data
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)
        if discovered_devices:
            devices = discovered_devices.values()
        else:
            _LOGGER.warning("⚠️ Using fallback: discovered_devices only.")
            devices = [(device, None) for device in scanner.discovered_devices]

        device_list = []

        _LOGGER.info(f"🔍 Found {len(devices)} Bluetooth devices.")  # Log number of devices

        for device, adv_data in devices:
            try:
                # Extract all available attributes from BLEDevice
                device_attributes = {
                    "address": getattr(device, "address", "Unknown"),
                    "name": getattr(device, "name", "Unknown"),
                    "details": getattr(device, "details", {}),
                    "id": getattr(device, "id", "Unknown"),
                    "rssi": getattr(device, "rssi", "Unknown"),  # Deprecated, but used for now
                    "metadata": getattr(device, "metadata", {}),
                }

                # Extract all available attributes from AdvertisementData
                adv_attributes = {
                    "local_name": getattr(adv_data, "local_name", "Unknown"),
                    "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
                    "service_uuids": getattr(adv_data, "service_uuids", []),
                    "service_data": _serialize_bytes(getattr(adv_data, "service_data", {})),
                    "manufacturer_data": _serialize_bytes(getattr(adv_data, "manufacturer_data", {})),
                    "rssi": getattr(adv_data, "rssi", getattr(device, "rssi", "Unknown")),
                    "tx_power": getattr(adv_data, "tx_power", "Unknown"),
                }

                # Log raw device data in JSON-safe format
                raw_data_log = {
                    "BLEDevice": device_attributes,
                    "AdvertisementData": adv_attributes,
                }
                _LOGGER.info(f"📡 RAW DEVICE DATA:\n{json.dumps(raw_data_log, indent=4, default=str)}")

                # Append to device list
                device_list.append({
                    "name": device_attributes["name"],
                    "mac": device_attributes["address"],
                    "rssi": adv_attributes["rssi"],
                    "manufacturer": adv_attributes["manufacturer"],
                    "service_uuids": adv_attributes["service_uuids"],
                    "service_data": adv_attributes["service_data"],
                    "manufacturer_data": adv_attributes["manufacturer_data"],
                    "tx_power": adv_attributes["tx_power"],
                })
            except Exception as e:
                _LOGGER.warning(f"⚠️ Failed to log raw device data: {e}")

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error discovering Bluetooth devices: {e}")
        return []

def _serialize_bytes(data):
    """Convert bytearray or bytes to JSON serializable format."""
    if isinstance(data, (bytes, bytearray)):
        return list(data)  # Convert bytearray to a list of integers
    elif isinstance(data, dict):
        return {key: _serialize_bytes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_bytes(item) for item in data]
    return data






 











































def pair_device(mac_address):
    """Simulate pairing with a Bluetooth device."""
    try:
        # Replace this with actual pairing logic
        _LOGGER.debug(f"Simulated pairing with {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error pairing with {mac_address}: {e}")
        return False

def connect_device(mac_address):
    """Simulate connecting to a Bluetooth device."""
    try:
        # Replace this with actual connection logic
        _LOGGER.debug(f"Simulated connecting to {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error connecting to {mac_address}: {e}")
        return False

def disconnect_device(mac_address):
    """Simulate disconnecting from a Bluetooth device."""
    try:
        # Replace this with actual disconnection logic
        _LOGGER.debug(f"Simulated disconnecting from {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error disconnecting from {mac_address}: {e}")
        return False
