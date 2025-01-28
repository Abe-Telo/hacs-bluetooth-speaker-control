from homeassistant.components.bluetooth import async_get_scanner
import logging

_LOGGER = logging.getLogger(__name__) 

 

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("Bluetooth scanner not available.")
            return []

        devices = scanner.discovered_devices
        device_list = []

        for device in devices:
            device_type = "Unknown"
            icon = "🚀"  # Default icon

            # Use name-based detection to assign type and icons
            name_lower = device.name.lower() if device.name else ""

            if "headphone" in name_lower:
                device_type = "Headphone"
                icon = "mdi:headphones"
            elif "speaker" in name_lower or "music" in name_lower:
                device_type = "Speaker"
                icon = "mdi:speaker"
            elif "tv" in name_lower or "display" in name_lower:
                device_type = "TV"
                icon = "mdi:television"
            elif "phone" in name_lower or "mobile" in name_lower:
                device_type = "Phone"
                icon = "mdi:cellphone"
            elif "watch" in name_lower or "wearable" in name_lower:
                device_type = "Wearable"
                icon = "mdi:watch"
            elif "keyboard" in name_lower:
                device_type = "Keyboard"
                icon = "mdi:keyboard"
            elif "mouse" in name_lower:
                device_type = "Mouse"
                icon = "mdi:mouse"

            rssi = getattr(device, "rssi", "Unknown")
            manufacturer = getattr(device, "manufacturer", "Unknown")
            uuids = getattr(device, "service_uuids", [])

            device_list.append({
                "name": device.name or "Unknown",
                "mac": device.address,
                "type": device_type,
                "icon": icon,  # Store the correct icon for later use
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids,
            })

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
