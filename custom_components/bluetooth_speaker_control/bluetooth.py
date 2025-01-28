import json
import logging
from homeassistant.components.bluetooth import async_get_scanner

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner not available.")
            return []

        # 🔍 Try getting discovered devices with advertisement data, fallback if unavailable
        try:
            discovered_devices = scanner.discovered_devices_and_advertisement_data
        except AttributeError:
            _LOGGER.warning("⚠️ `discovered_devices_and_advertisement_data` is not available. Falling back to `discovered_devices`.")
            discovered_devices = {device.address: (device, {}) for device in scanner.discovered_devices}

        if not discovered_devices:
            _LOGGER.warning("⚠️ No Bluetooth devices found.")
            return []

        device_list = []

        for device, adv_data in discovered_devices.values():
            # 🚀 LOG RAW DEVICE DATA
            raw_device_data = json.dumps(device.__dict__, indent=4, default=str)
            raw_adv_data = json.dumps(adv_data.__dict__, indent=4, default=str)
            _LOGGER.debug(f"🔍 RAW DEVICE DATA:\n{raw_device_data}")
            _LOGGER.debug(f"📡 RAW ADVERTISEMENT DATA:\n{raw_adv_data}")

            # Extracting attributes safely
            name = device.name or adv_data.get("local_name", "Unknown")
            mac = device.address
            manufacturer = adv_data.get("manufacturer", "Unknown")
            rssi = adv_data.get("rssi", "Unknown")
            uuids = adv_data.get("service_uuids", [])

            # 🔹 Detect device type and assign an icon
            device_type, icon = detect_device_type(name)

            # 🚀 Log final structured device data
            formatted_data = {
                "name": name,
                "mac": mac,
                "type": device_type,
                "icon": icon,
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids,
            }
            _LOGGER.info(f"✅ PROCESSED DEVICE DATA:\n{json.dumps(formatted_data, indent=4)}")

            device_list.append(formatted_data)

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error discovering Bluetooth devices: {e}")
        return []


def detect_device_type(name):
    """Detects the device type based on its name and assigns an icon."""
    device_type = "Unknown"
    icon = "🔵"  # Default icon for unknown Bluetooth devices
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
        icon = "🖱️(Not Supported)"
    elif "car" in name_lower or "vehicle" in name_lower:
        device_type = "Car Audio"
        icon = "🚗"
    elif "printer" in name_lower:
        device_type = "Printer"
        icon = "🖨️(Not Supported)"
    elif "tablet" in name_lower or "ipad" in name_lower:
        device_type = "Tablet"
        icon = "📟"
    elif "camera" in name_lower:
        device_type = "Camera"
        icon = "📷"
    elif "game" in name_lower or "controller" in name_lower:
        device_type = "Game Controller"
        icon = "🎮"
    elif "smart" in name_lower:
        device_type = "Smart Device"
        icon = "🏠"
    elif "fitness" in name_lower or "tracker" in name_lower:
        device_type = "Fitness Tracker"
        icon = "🏃"
    elif "drone" in name_lower:
        device_type = "Drone"
        icon = "🛸(Not Supported)"
    elif "hub" in name_lower or "gateway" in name_lower:
        device_type = "Hub"
        icon = "📡"
    elif "sensor" in name_lower or "detector" in name_lower:
        device_type = "Sensor"
        icon = "📍(Not Supported)"
    elif "light" in name_lower or "bulb" in name_lower:
        device_type = "Smart Light"
        icon = "💡(Not Supported)"

    return device_type, icon








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
