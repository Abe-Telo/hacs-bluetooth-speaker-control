import logging
import json
 
from homeassistant.components.bluetooth import (
    async_get_discovered_devices,
    async_register_callback,
    BluetoothScanningMode,
    BluetoothChange,
)

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass, timeout=5):
    """Discover nearby Bluetooth devices."""
    _LOGGER.info("🔍 Starting Bluetooth scan...")

    discovered_devices = []

    def device_found(service_info, change):
        """Callback when a device is found."""
        device = {
            "name": service_info.name or "Unknown",
            "mac": service_info.address,
            "rssi": getattr(service_info, "rssi", -100),
            "service_uuids": service_info.service_uuids or [],
        }
        _LOGGER.info(f"📡 Found Bluetooth device: {device}")
        discovered_devices.append(device)

    try:
        _LOGGER.info("📡 Registering Bluetooth scan callback...")
        stop_scan = async_register_callback(
            hass,
            device_found,
            mode=BluetoothScanningMode.ACTIVE,  # Fix: Provide mode parameter
        )

        _LOGGER.info(f"⏳ Waiting {timeout} seconds for scan results...")
        await hass.async_create_task(hass.loop.run_in_executor(None, lambda: hass.async_add_executor_job(stop_scan)))

    except Exception as e:
        _LOGGER.error(f"🔥 Error during Bluetooth scan: {e}")

    if not discovered_devices:
        _LOGGER.warning("⚠️ No Bluetooth devices found.")

    return discovered_devices


def _process_discovered_devices(discovered_devices):
    """Processes and formats discovered Bluetooth devices."""
    device_list = []
    _LOGGER.info(f"✅ Found {len(discovered_devices)} Bluetooth devices.")

    for device, adv_data in discovered_devices.items():
        try:
            device_data = {
                **extract_ble_device(device),
                **extract_adv_data(adv_data),
            }
            device_list.append(device_data)

            _LOGGER.debug("📡 Device discovered: %s", json.dumps(device_data, indent=4))

        except Exception as e:
            _LOGGER.error(f"⚠️ Error processing device {device}: {e}")

    return device_list

def extract_adv_data(adv_data):
    """Extract attributes from AdvertisementData safely."""
    if adv_data is None:
        return {
            "local_name": "Unknown",
            "manufacturer": "Unknown",
            "service_uuids": [],
            "service_data": {},
            "manufacturer_data": {},
            "rssi": -100,
            "tx_power": "Unknown",
        }

    return {
        "local_name": getattr(adv_data, "local_name", "Unknown"),
        "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
        "service_uuids": getattr(adv_data, "service_uuids", []),
        "service_data": _serialize_bytes(getattr(adv_data, "service_data", {})),
        "manufacturer_data": _serialize_bytes(getattr(adv_data, "manufacturer_data", {})),
        "rssi": getattr(adv_data, "rssi", -100),
        "tx_power": getattr(adv_data, "tx_power", "Unknown"),
    }

def extract_ble_device(device):
    """Extract attributes from BLEDevice safely."""
    return {
        "name": getattr(device, "name", "Unknown"),
        "mac": getattr(device, "address", "Unknown"),
        "details": str(getattr(device, "details", {})),
        "id": getattr(device, "id", "Unknown"),
    }

def _serialize_bytes(data):
    """Convert bytearray or bytes to JSON serializable format."""
    if isinstance(data, (bytes, bytearray)):
        return list(data)
    elif isinstance(data, dict):
        return {key: _serialize_bytes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_bytes(item) for item in data]
    return data

def pair_device(mac_address):
    """Simulate pairing with a Bluetooth device."""
    try:
        _LOGGER.debug(f"Simulated pairing with {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error pairing with {mac_address}: {e}")
        return False

def connect_device(mac_address):
    """Simulate connecting to a Bluetooth device."""
    try:
        _LOGGER.debug(f"Simulated connecting to {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error connecting to {mac_address}: {e}")
        return False

def disconnect_device(mac_address):
    """Simulate disconnecting from a Bluetooth device."""
    try:
        _LOGGER.debug(f"Simulated disconnecting from {mac_address}")
        return True
    except Exception as e:
        _LOGGER.error(f"Error disconnecting from {mac_address}: {e}")
        return False
