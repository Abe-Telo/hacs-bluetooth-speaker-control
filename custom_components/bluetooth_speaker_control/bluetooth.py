from homeassistant.components.bluetooth import async_get_scanner
import logging

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        # Check if the async_get_scanner method is supported in this Home Assistant version
        if not hasattr(hass.components.bluetooth, "async_get_scanner"):
            _LOGGER.error("Bluetooth scanner is not supported in this Home Assistant version.")
            return []

        # Get the Bluetooth scanner
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner not available.")
            return []

        # Attempt to use discovered_devices_and_advertisement_data
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)

        if not discovered_devices:
            _LOGGER.warning("⚠️ Using fallback: discovered_devices only.")
            discovered_devices = {
                device: {"rssi": getattr(device, "rssi", -100)}  # Include at least RSSI as data
                for device in scanner.discovered_devices
            }

        device_list = []

        _LOGGER.info(f"🔍 Found {len(discovered_devices)} Bluetooth devices.")

        for device, adv_data in discovered_devices.items():
            # Process AdvertisementData attributes
            adv_attributes = extract_adv_data(adv_data)

            # Process BLEDevice attributes
            device_attributes = extract_ble_device(device)

            # Combine both attributes
            device_data = {**device_attributes, **adv_attributes}

            # Log raw device data safely
            _LOGGER.debug("📡 RAW DEVICE DATA: %s", device_data)

            # Append to device list
            device_list.append(device_data)

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error discovering Bluetooth devices: {e}")
        return []


def extract_adv_data(adv_data):
    """Extract attributes from AdvertisementData safely."""
    if adv_data is None:
        return {
            "local_name": "Unknown",
            "manufacturer": "Unknown",
            "service_uuids": [],
            "service_data": {},
            "manufacturer_data": {},
            "rssi": -100,  # Dummy RSSI value
            "tx_power": "Unknown",
        }
    return {
        "local_name": getattr(adv_data, "local_name", "Unknown"),
        "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
        "service_uuids": getattr(adv_data, "service_uuids", []),
        "service_data": _serialize_bytes(getattr(adv_data, "service_data", {})),
        "manufacturer_data": _serialize_bytes(getattr(adv_data, "manufacturer_data", {})),
        "rssi": getattr(adv_data, "rssi", -100),  # Use RSSI from AdvertisementData
        "tx_power": getattr(adv_data, "tx_power", "Unknown"),
    }


def extract_ble_device(device):
    """Extract attributes from BLEDevice safely."""
    return {
        "name": getattr(device, "name", "Unknown"),
        "mac": getattr(device, "address", "Unknown"),
        "details": str(getattr(device, "details", {})),
        "id": getattr(device, "id", "Unknown"),
    }


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
