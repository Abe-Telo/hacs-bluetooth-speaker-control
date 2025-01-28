from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)


async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        # Get the scanner object
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("Bluetooth scanner not available.")
            return []

        # Attempt to fetch advertisement data and discovered devices
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)
        if not discovered_devices:
            _LOGGER.warning("Using fallback: discovered_devices only.")
            devices = scanner.discovered_devices
        else:
            devices = discovered_devices.values()

        device_list = []

        for item in devices:
            # Separate device and advertisement data
            if isinstance(item, tuple):  # If `discovered_devices_and_advertisement_data`
                device, adv_data = item
            else:
                device, adv_data = item, None  # Fallback if only device is available

            # Advertisement attributes
            adv_attributes = {
                "local_name": getattr(adv_data, "local_name", "Unknown"),
                "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
                "service_uuids": getattr(adv_data, "service_uuids", []),
                "service_data": _serialize_bytes(getattr(adv_data, "service_data", {})),
                "manufacturer_data": _serialize_bytes(getattr(adv_data, "manufacturer_data", {})),
                "rssi": getattr(adv_data, "rssi", "Unknown"),
                "tx_power": getattr(adv_data, "tx_power", "Unknown"),
            }

            # BLEDevice attributes
            device_attributes = {
                "address": getattr(device, "address", "Unknown"),
                "name": getattr(device, "name", adv_attributes["local_name"] or "Unknown"),
                "rssi": getattr(device, "rssi", adv_attributes["rssi"]),
                "details": getattr(device, "details", {}),
                "id": getattr(device, "id", "Unknown"),
            }

            # Log raw data
            try:
                raw_data_log = {
                    "device": device_attributes,
                    "advertisement": adv_attributes,
                }
                _LOGGER.info(f"📡 RAW DEVICE DATA:\n{json.dumps(raw_data_log, indent=4)}")
            except TypeError as e:
                _LOGGER.warning(f"⚠️ Failed to log raw data: {e}")

            # Append processed data
            device_list.append({
                "name": device_attributes["name"],
                "mac": device_attributes["address"],
                "type": "Unknown",  # Placeholder for detection logic
                "rssi": device_attributes["rssi"],
                "manufacturer": adv_attributes["manufacturer"],
                "service_uuids": adv_attributes["service_uuids"],
                "service_data": adv_attributes["service_data"],
                "manufacturer_data": adv_attributes["manufacturer_data"],
                "tx_power": adv_attributes["tx_power"],
            })

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error discovering Bluetooth devices: {e}")
        return []


def _serialize_bytes(data):
    """Convert bytearray or bytes to JSON serializable format."""
    if isinstance(data, (bytes, bytearray)):
        return list(data)
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
