from homeassistant.components.bluetooth import async_get_scanner
import logging
import json  # For structured logging

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("Bluetooth scanner not available.")
            return []

        devices = scanner.discovered_devices  # ✅ Use the supported API
        device_list = []

        for device in devices:
            try:
                # Log raw device data
                raw_data = json.dumps(device.__dict__, indent=4, default=str)
                _LOGGER.info(f"🔍 RAW DEVICE DATA:\n{raw_data}")
            except Exception as e:
                _LOGGER.warning(f"⚠️ Failed to log raw device data: {e}")

            # Extract device attributes
            name = device.name or "Unknown"
            mac = device.address
            rssi = getattr(device, "rssi", "Unknown")  # ❌ Deprecated but functional for now
            uuids = getattr(device, "service_uuids", [])
            manufacturer = "Unknown"  # Replace with actual extraction logic if needed

            # Determine device type and icon
            device_type = "Unknown"
            icon = "🔵"  # Default Bluetooth icon
            name_lower = name.lower()

            if "headphone" in name_lower:
                device_type = "Headphone"
                icon = "🎧"
            elif "speaker" in name_lower or "music" in name_lower:
                device_type = "Speaker"
                icon = "🔊"
            elif "tv" in name_lower or "display" in name_lower:
                device_type = "TV"
                icon = "📺"
            elif "phone" in name_lower or "mobile" in name_lower:
                device_type = "Phone"
                icon = "📱"
            elif "watch" in name_lower or "wearable" in name_lower:
                device_type = "Wearable"
                icon = "⌚"

            # Add processed device data to the list
            device_list.append({
                "name": name,
                "mac": mac,
                "type": device_type,
                "icon": icon,
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids,
            })

        _LOGGER.info(f"✅ PROCESSED DEVICE LIST:\n{json.dumps(device_list, indent=4)}")
        return device_list

    except Exception as e:
        _LOGGER.error(f"Error discovering Bluetooth devices using Home Assistant API: {e}")
        return []




































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
