from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner not available.")
            return []

        devices = scanner.discovered_devices
        if not devices:
            _LOGGER.warning("⚠️ No Bluetooth devices found.")
            return []

        device_list = []

        _LOGGER.info("🔍 Scanning for Bluetooth devices...")

        for device in devices:
            # 🚀 LOG RAW DEVICE DATA (Everything received)
            raw_data = {
                "name": getattr(device, "name", "Unknown"),
                "mac": getattr(device, "address", "Unknown"),
                "rssi": getattr(device, "rssi", "Unknown"),
                "uuids": getattr(device, "service_uuids", []),
            }
            _LOGGER.info(f"🔵 Bluetooth RAW DEVICE DATA:\n{json.dumps(raw_data, indent=4)}")

            # Default values
            device_type = "Unknown"
            icon = "🔵"  # Default Bluetooth icon
            manufacturer = "Unknown"
            rssi = getattr(device, "rssi", "Unknown")  # ✅ Keeping BLEDevice.rssi for now
            uuids = getattr(device, "service_uuids", [])

            # Use name-based detection to assign type and icons
            name_lower = raw_data["name"].lower() if raw_data["name"] else ""

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

            # Construct device dictionary
            formatted_data = {
                "name": raw_data["name"],
                "mac": raw_data["mac"],
                "type": device_type,
                "icon": icon,  # Store the correct icon for later use
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids,
            }

            # 🚀 LOG FINAL PROCESSED DEVICE DATA
            _LOGGER.info(f"✅ Bluetooth PROCESSED DEVICE DATA:\n{json.dumps(formatted_data, indent=4)}")

            device_list.append(formatted_data)

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error discovering Bluetooth devices using Home Assistant API: {e}")
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
