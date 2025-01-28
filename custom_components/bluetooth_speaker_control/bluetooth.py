from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        # Get the Bluetooth scanner object
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner not available.")
            return []

        # Attempt to fetch advertisement data and discovered devices
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)
        if not discovered_devices:
            _LOGGER.warning("⚠️ Using fallback: discovered_devices only.")
            devices = [(device, None) for device in scanner.discovered_devices]
        else:
            devices = discovered_devices.values()

        device_list = []

        # Log the number of devices found
        _LOGGER.info(f"🔍 Found {len(devices)} Bluetooth devices.")

        for device, adv_data in devices:
            try:
                # Extract attributes safely without using `__dict__`
                device_data = {
                    "address": getattr(device, "address", "Unknown"),
                    "name": getattr(device, "name", "Unknown"),
                    "rssi": getattr(device, "rssi", "Unknown"),
                    "details": str(getattr(device, "details", "Unknown")),
                    "id": getattr(device, "id", "Unknown"),
                }

                # Extract advertisement data safely
                adv_data_data = {
                    "local_name": getattr(adv_data, "local_name", "Unknown") if adv_data else "Unknown",
                    "manufacturer": getattr(adv_data, "manufacturer", "Unknown") if adv_data else "Unknown",
                    "service_uuids": getattr(adv_data, "service_uuids", []) if adv_data else [],
                }

                # Log the device and advertisement data
                _LOGGER.info(f"📡 Device Data:\n{json.dumps(device_data, indent=4)}")
                _LOGGER.info(f"📡 Advertisement Data:\n{json.dumps(adv_data_data, indent=4)}")

                # Append processed data to the device list
                device_list.append({
                    "name": device_data["name"],
                    "mac": device_data["address"],
                    "type": "Unknown",  # Placeholder for detection logic
                    "rssi": device_data["rssi"],
                    "manufacturer": adv_data_data["manufacturer"],
                    "service_uuids": adv_data_data["service_uuids"],
                })

            except Exception as e:
                _LOGGER.warning(f"⚠️ Error processing device attributes: {e}")

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
