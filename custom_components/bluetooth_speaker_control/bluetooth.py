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

        # Get discovered devices and advertisement data if supported
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)
        if not discovered_devices:
            _LOGGER.warning("⚠️ Using fallback: discovered_devices only.")
            devices = [(device, None) for device in scanner.discovered_devices]
        else:
            devices = discovered_devices.values()

        device_list = []

        _LOGGER.info(f"🔍 Found {len(devices)} Bluetooth devices.")  # Log number of devices

        for device, adv_data in devices:
            try:
                # Dynamically log all attributes from BLEDevice
                _LOGGER.info(f"📡 BLEDevice Attributes:\n{json.dumps(device.__dict__, indent=4, default=str)}")

                # Log AdvertisementData if available
                if adv_data:
                    _LOGGER.info(f"📡 AdvertisementData Attributes:\n{json.dumps(adv_data.__dict__, indent=4, default=str)}")
                else:
                    _LOGGER.info("📡 AdvertisementData not available for this device.")

                # Extract specific attributes as a fallback for display
                device_data = {
                    "address": getattr(device, "address", "Unknown"),
                    "name": getattr(device, "name", "Unknown"),
                    "rssi": getattr(device, "rssi", "Unknown"),  # Deprecated, fallback
                    "local_name": getattr(adv_data, "local_name", "Unknown") if adv_data else "Unknown",
                    "manufacturer": getattr(adv_data, "manufacturer", "Unknown") if adv_data else "Unknown",
                    "service_uuids": getattr(adv_data, "service_uuids", []) if adv_data else [],
                }

                # Add to the device list
                device_list.append(device_data)

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
