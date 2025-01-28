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

        # Get both devices and advertisement data (newer Home Assistant versions)
        discovered_devices = scanner.discovered_devices_and_advertisement_data

        device_list = []

        for device, adv_data in discovered_devices.values():
            name = device.name or adv_data.local_name or "Unknown"
            mac = device.address
            manufacturer = adv_data.manufacturer or "Unknown"
            rssi = adv_data.rssi if adv_data.rssi else "Unknown"
            uuids = adv_data.service_uuids or []

            # **Determine Device Type and Icon**
            device_type = "Unknown"
            icon = "❓"  # Default unknown emoji/icon
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
            elif "keyboard" in name_lower:
                device_type = "Keyboard"
                icon = "⌨️"
            elif "mouse" in name_lower:
                device_type = "Mouse"
                icon = "🖱️"
            elif "car" in name_lower or "auto" in name_lower:
                device_type = "Car System"
                icon = "🚗"

            # **Format the discovered device**
            device_list.append({
                "name": name,
                "mac": mac,
                "type": device_type,
                "icon": icon,  # Use the icon determined above
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
