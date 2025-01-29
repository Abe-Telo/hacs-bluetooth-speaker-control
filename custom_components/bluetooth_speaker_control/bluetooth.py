from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        _LOGGER.info("🔍 Starting Bluetooth device discovery...")

        # Get the Bluetooth scanner
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner is unavailable. Ensure the Bluetooth integration is set up correctly.")
            return []

        # Attempt to use discovered_devices_and_advertisement_data if available
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)

        if not discovered_devices:
            _LOGGER.warning("⚠️ Using fallback to scanner.discovered_devices.")
            discovered_devices = {
                device: {"rssi": getattr(device, "rssi", -100)}  # Add at least RSSI
                for device in scanner.discovered_devices
            }

        if not discovered_devices:
            _LOGGER.warning(
                "⚠️ No devices discovered. Ensure devices are in discoverable mode and within range of the Bluetooth adapter."
            )
            return []

        device_list = []

        _LOGGER.info(f"🔍 Found {len(discovered_devices)} Bluetooth devices.")

        for device, adv_data in discovered_devices.items():
            try:
                # Process the device and advertisement data
                device_data = {
                    **extract_ble_device(device),
                    **extract_adv_data(adv_data),
                }
                device_list.append(device_data)

                # Log the discovered device for debugging
                _LOGGER.debug("📡 Device discovered: %s", json.dumps(device_data, indent=4))

            except Exception as e:
                _LOGGER.error(f"⚠️ Error processing device {device}: {e}")

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error during Bluetooth discovery: {e}")
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

# --- 🔗 Pairing, Connecting, Disconnecting ---

def pair_device(mac_address):
    """Simulate pairing with a Bluetooth device."""
    try:
        _LOGGER.debug(f"🔗 Simulated pairing with {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"❌ Error pairing with {mac_address}: {e}")
        return False

def connect_device(mac_address):
    """Simulate connecting to a Bluetooth device."""
    try:
        _LOGGER.debug(f"🔄 Simulated connecting to {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"❌ Error connecting to {mac_address}: {e}")
        return False

def disconnect_device(mac_address):
    """Simulate disconnecting from a Bluetooth device."""
    try:
        _LOGGER.debug(f"🔌 Simulated disconnecting from {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"❌ Error disconnecting from {mac_address}: {e}")
        return False
