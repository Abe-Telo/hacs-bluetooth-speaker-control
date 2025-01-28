from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        # Get the scanner object
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("Bluetooth scanner not available.")
            return []

        # Attempt to fetch advertisement data and discovered devices
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)
        if not discovered_devices:
            _LOGGER.warning("Using fallback: discovered_devices only.")
            devices = scanner.discovered_devices
        else:
            devices = discovered_devices.values()

        device_list = []

        for item in devices:
            # Separate device and advertisement data
            if isinstance(item, tuple):  # In case of `discovered_devices_and_advertisement_data`
                device, adv_data = item
            else:
                device, adv_data = item, None  # Fallback if only device is available

            # Collect advertisement data
            adv_attributes = {
                "local_name": getattr(adv_data, "local_name", "Unknown"),
                "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
                "service_uuids": getattr(adv_data, "service_uuids", []),
                "service_data": getattr(adv_data, "service_data", {}),
                "manufacturer_data": getattr(adv_data, "manufacturer_data", {}),
                "rssi": getattr(adv_data, "rssi", "Unknown"),
                "tx_power": getattr(adv_data, "tx_power", "Unknown"),
            }

            # Collect BLEDevice data
            device_attributes = {
                "address": getattr(device, "address", "Unknown"),
                "name": getattr(device, "name", adv_attributes["local_name"] or "Unknown"),
                "rssi": getattr(device, "rssi", adv_attributes["rssi"]),
                "details": getattr(device, "details", {}),
                "metadata": getattr(device, "metadata", {}),
                "id": getattr(device, "id", "Unknown"),
            }

            # Combine and log raw data
            raw_data_log = {
                "device": device_attributes,
                "advertisement": adv_attributes,
            }
            _LOGGER.info(f"📡 RAW DEVICE DATA:\n{json.dumps(raw_data_log, indent=4)}")

            # Construct processed device entry for the final list
            device_list.append({
                "name": device_attributes["name"],
                "mac": device_attributes["address"],
                "type": "Unknown",  # You can enhance this with detection logic (e.g., name-based)
                "rssi": device_attributes["rssi"],
                "manufacturer": adv_attributes["manufacturer"],
                "service_uuids": adv_attributes["service_uuids"],
                "service_data": adv_attributes["service_data"],
                "manufacturer_data": adv_attributes["manufacturer_data"],
                "tx_power": adv_attributes["tx_power"],
            })

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
