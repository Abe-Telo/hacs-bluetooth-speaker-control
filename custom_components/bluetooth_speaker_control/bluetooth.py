from homeassistant.components.bluetooth import async_get_scanner
import logging
import json  # For structured logging

_LOGGER = logging.getLogger(__name__) 

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner not available.")
            return []

        devices = scanner.discovered_devices
        device_list = []

        _LOGGER.info(f"🔍 **Found {len(devices)} Bluetooth devices**")

        for device in devices:
            # 🚀 LOG RAW DEVICE DATA
            try:
                raw_device_data = json.dumps(device.__dict__, indent=4, default=str)
                _LOGGER.info(f"📡 **RAW BLUETOOTH DEVICE DATA:**\n{raw_device_data}")
            except Exception as e:
                _LOGGER.warning(f"⚠️ Failed to log raw device data: {e}")

            # Default values
            device_type = "Unknown"
            icon = "🔵"  # Default Bluetooth icon
            manufacturer = getattr(device, "manufacturer", "Unknown")

            # 🔥 Check if `AdvertisementData` is available
            adv_data = getattr(device, "advertisement_data", None)
            use_adv_rssi = False  # Default to BLEDevice.rssi
            
            if adv_data:
                use_adv_rssi = hasattr(adv_data, "rssi")  # Check if `rssi` is present in AdvertisementData

            # Choose the correct RSSI source
            if use_adv_rssi:
                rssi = adv_data.rssi  # ✅ Use AdvertisementData.rssi if available
                _LOGGER.info("📶 **Using AdvertisementData.rssi**")
            else:
                rssi = getattr(device, "rssi", "Unknown")  # ❌ Fall back to BLEDevice.rssi
                _LOGGER.warning("⚠️ **Using BLEDevice.rssi (Deprecated). AdvertisementData.rssi NOT found.**")

            # Get UUIDs
            uuids = getattr(device, "service_uuids", [])

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

            # Construct device dictionary
            processed_device = {
                "name": device.name or "Unknown",
                "mac": device.address,
                "type": device_type,
                "icon": icon,  # Store the correct icon for later use
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids,
            }

            # ✅ Log processed device data
            _LOGGER.info(f"✅ **PROCESSED DEVICE DATA:**\n{json.dumps(processed_device, indent=4)}")

            device_list.append(processed_device)

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
