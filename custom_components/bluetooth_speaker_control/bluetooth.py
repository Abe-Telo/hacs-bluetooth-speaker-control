from homeassistant.components.bluetooth import async_get_scanner
import logging
import json  # For pretty-printing structured data

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("Bluetooth scanner not available.")
            return []

        # Use discovered_devices_and_advertisement_data for better insights
        discovered_devices = scanner.discovered_devices_and_advertisement_data
        device_list = []

        for device, adv_data in discovered_devices.values():
            # Log raw data for the device and advertisement data
            try:
                _LOGGER.info("🔍 RAW DEVICE DATA:")
                _LOGGER.info(json.dumps(device.__dict__, indent=4, default=str))

                _LOGGER.info("📡 RAW ADVERTISEMENT DATA:")
                _LOGGER.info(json.dumps(adv_data.__dict__, indent=4, default=str))
            except AttributeError as e:
                _LOGGER.warning(f"⚠️ Failed to log raw device data: {e}")

            # Extract relevant data
            rssi = adv_data.rssi if adv_data else "Unknown"

            # Default values
            device_type = "Unknown"
            icon = "🔵"  # Default Bluetooth icon
            manufacturer = adv_data.manufacturer if adv_data else "Unknown"
            uuids = adv_data.service_uuids if adv_data else []

            # Use name-based detection to assign type and icons
            name_lower = device.name.lower() if device.name else ""

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

            # Log processed device data
            formatted_data = {
                "name": device.name or "Unknown",
                "mac": device.address,
                "type": device_type,
                "icon": icon,
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids,
            }
            _LOGGER.info("✅ PROCESSED DEVICE DATA:")
            _LOGGER.info(json.dumps(formatted_data, indent=4))

            # Append to device list
            device_list.append(formatted_data)

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error discovering Bluetooth devices: {e}")
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
