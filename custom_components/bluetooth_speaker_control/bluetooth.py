import logging
import asyncio
import json
import base64

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.bluetooth import (
    async_register_callback,
    async_discovered_service_info,
    BluetoothScanningMode,
    BluetoothChange,
)

_LOGGER = logging.getLogger(__name__)

BLUETOOTH_SIG_COMPANIES = {
    6: "Microsoft",
    76: "Apple, Inc.",
    89: "Garmin International, Inc.",
    117: "Google",
    152: "Samsung Electronics Co. Ltd.",
    4096: "Sony Corporation",
    4961: "Bose Corporation",
    1177: "Logitech Inc.",
    3052: "Fitbit, Inc.",
    6171: "Meta Platforms, Inc.",
}

def decode_device_name(name_bytes):
    """Attempt to decode a device name from multiple encodings."""
    if not name_bytes or len(name_bytes) < 2:
        return None

    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            decoded = name_bytes.decode(encoding).strip()
            if all(32 <= ord(c) < 127 for c in decoded):
                return decoded
        except UnicodeDecodeError:
            continue

    return f"[ENCODED] {base64.b64encode(name_bytes).decode()}"

def extract_friendly_name(service_info):
    """Extract a friendly name from available advertisement or manufacturer data."""
    if hasattr(service_info, "advertisement") and service_info.advertisement:
        if hasattr(service_info.advertisement, "local_name") and service_info.advertisement.local_name:
            return service_info.advertisement.local_name.strip()
    
    manufacturer_data = service_info.manufacturer_data or {}
    for key, value in manufacturer_data.items():
        if len(value) > 2:  # Ensure we have enough data to slice
            possible_name = decode_device_name(value[2:])
            if possible_name:
                return possible_name
    return None

def serialize_service_info(service_info):
    """Convert BluetoothServiceInfoBleak to a JSON-serializable format."""
    try:
        return {
            "name": service_info.name,
            "address": service_info.address,
            "rssi": service_info.rssi,
            "manufacturer_data": {key: base64.b64encode(value).decode() for key, value in service_info.manufacturer_data.items()},
            "service_data": {key: base64.b64encode(value).decode() for key, value in service_info.service_data.items()} if service_info.service_data else {},
            "service_uuids": service_info.service_uuids or [],
            "source": service_info.source,
            "connectable": service_info.connectable,
            "tx_power": service_info.tx_power if service_info.tx_power is not None else "Unknown",
        }
    except Exception as e:
        _LOGGER.error(f"🔥 Error serializing service info: {e}")
        return {}

def _format_device(service_info):
    """Extract relevant details from the discovered service info."""
    _LOGGER.debug(f"📡 Raw Service Info Attributes: {dir(service_info)}")
    try:
        _LOGGER.debug(f"📡 Full Service Info as_dict(): {json.dumps(serialize_service_info(service_info), indent=2)}")
    except Exception as e:
        _LOGGER.error(f"🔥 Error logging service info: {e}")

    device_name = extract_friendly_name(service_info) or service_info.name or service_info.address
    
    manufacturer_data = service_info.manufacturer_data or {}
    manufacturer_id = next(iter(manufacturer_data), None)
    manufacturer = BLUETOOTH_SIG_COMPANIES.get(manufacturer_id, f"Unknown (ID {manufacturer_id})")
    
    if device_name == service_info.address:
        device_name = f"{manufacturer} Device ({service_info.address[-5:]})"
    
    _LOGGER.info(f"🆔 Discovered Device: {json.dumps(serialize_service_info(service_info), indent=2)}")
    
    return {
        "name": device_name,
        "manufacturer": manufacturer,
        "mac_address": service_info.address,
        "rssi": service_info.rssi,
        "service_uuids": service_info.service_uuids,
    }

async def discover_bluetooth_devices(hass, timeout=7, passive_scanning=True):
    """Discover Bluetooth devices using Home Assistant's built-in discovery API."""
    _LOGGER.debug(f"🔍 Discovering Bluetooth devices (Passive: {passive_scanning})...")
    discovered_devices = []

    for service_info in async_discovered_service_info(hass):
        _LOGGER.debug(f"📡 Service Info: {json.dumps(serialize_service_info(service_info), indent=2)}")
        discovered_devices.append(_format_device(service_info))

    if discovered_devices:
        _LOGGER.info(f"✅ Found {len(discovered_devices)} devices before scanning: {json.dumps(discovered_devices, indent=2)}")
        return discovered_devices

    return discovered_devices

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the cache-clearing service in Home Assistant."""
    async def handle_clear_cache(call: ServiceCall) -> None:
        """Service call to clear the manufacturer cache."""
        _LOGGER.info("🗑️ Clearing manufacturer cache...")
    hass.services.async_register("bluetooth_speaker_control", "clear_cache", handle_clear_cache)
    return True






 


### **🔹 Extract Advertisement Data Properly**
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


### **🔹 Extract BLE Device Data Properly**
def extract_ble_device(device):
    """Extract attributes from BLEDevice safely."""
    return {
        "name": getattr(device, "name", "Unknown"),
        "mac": getattr(device, "address", "Unknown"),
        "details": str(getattr(device, "details", {})),
        "id": getattr(device, "id", "Unknown"),
    }


### **🔹 Helper Function for Serializing Byte Data**
def _serialize_bytes(data):
    """Convert bytearray or bytes to JSON serializable format."""
    if isinstance(data, (bytes, bytearray)):
        return list(data)
    elif isinstance(data, dict):
        return {key: _serialize_bytes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_bytes(item) for item in data]
    return data


### **🔹 Simulated Bluetooth Pairing, Connecting, Disconnecting**
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
