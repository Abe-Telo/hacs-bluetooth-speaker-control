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

        # Attempt to fetch advertisement data and discovered devices
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)
        if not discovered_devices:
            _LOGGER.warning("⚠️ Using fallback: discovered_devices only.")
            devices = [(device, None) for device in scanner.discovered_devices]
        else:
            devices = discovered_devices.values()

        device_list = []

        _LOGGER.info(f"🔍 Found {len(devices)} Bluetooth devices.")

        for device, adv_data in devices:
            try:
                # Log all attributes of device and adv_data
                _LOGGER.info(f"📋 BLEDevice Attributes:\n{dir(device)}")
                if adv_data:
                    _LOGGER.info(f"📋 AdvertisementData Attributes:\n{dir(adv_data)}")

                # Safe extraction of rssi and other attributes
                rssi = getattr(adv_data, "rssi", getattr(device, "rssi", -100))  # Dummy value if unavailable
                adv_data_data = {
                    "local_name": getattr(adv_data, "local_name", "Unknown") if adv_data else "Unknown",
                    "manufacturer": getattr(adv_data, "manufacturer", "Unknown") if adv_data else "Unknown",
                    "service_uuids": getattr(adv_data, "service_uuids", []) if adv_data else [],
                    "rssi": rssi,
                }

                # BLEDevice attributes
                device_attributes = {
                    "address": getattr(device, "address", "Unknown"),
                    "name": getattr(device, "name", adv_data_data["local_name"] or "Unknown"),
                    "details": str(getattr(device, "details", {})),
                    "id": getattr(device, "id", "Unknown"),
                }

                # Log raw device and advertisement data
                raw_data_log = {
                    "device": device_attributes,
                    "advertisement": adv_data_data,
                }
                _LOGGER.info(f"📡 RAW DATA:\n{json.dumps(raw_data_log, indent=4)}")

                # Append processed data to the device list
                device_list.append({
                    "name": device_attributes["name"],
                    "mac": device_attributes["address"],
                    "type": "Unknown",  # Placeholder for detection logic
                    "rssi": rssi,
                    "manufacturer": adv_data_data["manufacturer"],
                    "service_uuids": adv_data_data["service_uuids"],
                })

            except Exception as e:
                _LOGGER.warning(f"⚠️ Error processing device attributes: {e}")

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
