from homeassistant.components.bluetooth import async_get_scanner
import logging

_LOGGER = logging.getLogger(__name__) 

DEVICE_TYPE_ICONS = {
    "Headphone": "mdi:headphones",
    "Music Player": "mdi:music-note",
    "Speaker": "mdi:speaker",
    "Unknown": "mdi:bluetooth",
}

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("Bluetooth scanner not available.")
            return []

        devices = scanner.discovered_devices_and_advertisement_data  # Corrected API usage

        if not devices:
            _LOGGER.warning("No Bluetooth devices found.")
            return []

        _LOGGER.debug(f"Discovered devices using Home Assistant Bluetooth API: {devices}")

        device_list = []
        for device, adv_data in devices.items():  # Extract BLEDevice & AdvertisementData
            device_type = "Unknown"
            icon = "mdi:bluetooth"

            # Determine device type based on name (simple logic, improve as needed)
            if device.name and "headphone" in device.name.lower():
                device_type = "Headphone"
                icon = "mdi:headphones"
            elif device.name and "music" in device.name.lower():
                device_type = "Music Player"
                icon = "mdi:speaker"

            # Fetch manufacturer safely from AdvertisementData
            manufacturer = (
                next(iter(adv_data.manufacturer_data.values()), "Unknown")
                if adv_data.manufacturer_data else "Unknown"
            )

            # Extract RSSI correctly from AdvertisementData
            rssi = adv_data.rssi if adv_data.rssi is not None else "Unknown"

            # Extract UUIDs from AdvertisementData
            uuids = adv_data.service_uuids or []

            device_list.append({
                "name": device.name or "Unknown",
                "mac": device.address,
                "type": device_type,
                "icon": icon,
                "rssi": rssi,
                "manufacturer": manufacturer,
                "uuids": uuids
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
