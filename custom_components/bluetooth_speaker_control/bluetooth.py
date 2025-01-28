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
            icon = "🔵"  # Default icon for unknown devices

            # Use name-based detection to assign type and icons
            name_lower = device.name.lower() if device.name else ""

            # Temporery Display all icons to see if it discovers Correct BT
            if "headphone" in name_lower:
                device_type = "Headphone"
                icon = "🎧"  # Headphone emoji
            elif "speaker" in name_lower or "music" in name_lower:
                device_type = "Speaker"
                icon = "🔊"  # Speaker emoji
            elif "tv" in name_lower or "display" in name_lower:
                device_type = "TV"
                icon = "📺"  # Television emoji
            elif "phone" in name_lower or "mobile" in name_lower:
                device_type = "Phone"
                icon = "📱"  # Mobile phone emoji
            elif "watch" in name_lower or "wearable" in name_lower:
                device_type = "Wearable"
                icon = "⌚"  # Watch emoji
            elif "keyboard" in name_lower:
                device_type = "Keyboard"
                icon = "⌨️"  # Keyboard emoji
            elif "mouse" in name_lower:
                device_type = "Mouse"
                icon = "🖱️(Not Supported)"  # Mouse emoji
            elif "car" in name_lower or "vehicle" in name_lower:
                device_type = "Car Audio"
                icon = "🚗"  # Car emoji
            elif "printer" in name_lower:
                device_type = "Printer"
                icon = "🖨️(Not Supported)"  # Printer emoji
            elif "tablet" in name_lower or "ipad" in name_lower:
                device_type = "Tablet"
                icon = "📟"  # Tablet emoji
            elif "camera" in name_lower:
                device_type = "Camera"
                icon = "📷"  # Camera emoji
            elif "game" in name_lower or "controller" in name_lower:
                device_type = "Game Controller"
                icon = "🎮"  # Game controller emoji
            elif "smart" in name_lower:
                device_type = "Smart Device"
                icon = "🏠"  # Smart home emoji
            elif "fitness" in name_lower or "tracker" in name_lower:
                device_type = "Fitness Tracker"
                icon = "🏃"  # Running emoji
            elif "drone" in name_lower:
                device_type = "Drone"
                icon = "🛸(Not Supported)"  # Drone emoji
            elif "hub" in name_lower or "gateway" in name_lower:
                device_type = "Hub"
                icon = "📡"  # Satellite emoji
            elif "sensor" in name_lower or "detector" in name_lower:
                device_type = "Sensor"
                icon = "📍(Not Supported)"  # Location pin emoji
            elif "light" in name_lower or "bulb" in name_lower:
                device_type = "Smart Light"
                icon = "💡(Not Supported)"  # Light bulb emoji

            # Extract additional device information
            rssi = getattr(device, "rssi", "Unknown")
            manufacturer = getattr(device, "manufacturer", "Unknown")
            uuids = getattr(device, "service_uuids", [])

            # Append device to the list
            device_list.append({
                "name": device.name or "Unknown",
                "mac": device.address,
                "type": device_type,
                "icon": icon,  # Emoji icon for display
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
