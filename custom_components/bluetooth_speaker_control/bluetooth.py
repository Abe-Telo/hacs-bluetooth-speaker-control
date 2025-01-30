import logging
import asyncio
import json
import base64
import aiohttp

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.bluetooth import (
    async_register_callback,
    async_discovered_service_info,
    BluetoothScanningMode,
    BluetoothChange,
)

_LOGGER = logging.getLogger(__name__)

BLUETOOTH_NUMBERS_DB = "https://raw.githubusercontent.com/NordicSemiconductor/bluetooth-numbers-database/refs/heads/master/"

BLUETOOTH_SIG_COMPANIES = {}
GAP_APPEARANCE = {}
SERVICE_UUIDS = {}
CHARACTERISTIC_UUIDS = {}

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


async def fetch_bluetooth_database():
    """Fetch and update the Bluetooth database from Nordic Semiconductor."""
    global BLUETOOTH_SIG_COMPANIES, GAP_APPEARANCE, SERVICE_UUIDS, CHARACTERISTIC_UUIDS
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BLUETOOTH_NUMBERS_DB + "decimal_ids.json") as response:
                BLUETOOTH_SIG_COMPANIES = await response.json()
            async with session.get(BLUETOOTH_NUMBERS_DB + "gap_appearance.json") as response:
                GAP_APPEARANCE = await response.json()
            async with session.get(BLUETOOTH_NUMBERS_DB + "service_uuids.json") as response:
                SERVICE_UUIDS = await response.json()
            async with session.get(BLUETOOTH_NUMBERS_DB + "characteristic_uuids.json") as response:
                CHARACTERISTIC_UUIDS = await response.json()
            _LOGGER.info("✅ Successfully updated Bluetooth database from Nordic Semiconductor")
        except Exception as e:
            _LOGGER.error(f"🔥 Error fetching Bluetooth database: {e}")


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
    """Extract a friendly name from advertisement or manufacturer data."""
    if hasattr(service_info, "advertisement") and service_info.advertisement:
        if hasattr(service_info.advertisement, "local_name") and service_info.advertisement.local_name:
            return service_info.advertisement.local_name.strip()
    
    manufacturer_data = service_info.manufacturer_data or {}
    for key, value in manufacturer_data.items():
        if len(value) > 2:
            possible_name = decode_device_name(value[2:])
            if possible_name:
                return possible_name
    return None


def get_device_type(appearance_id):
    """Retrieve device type from GAP Appearance database."""
    return GAP_APPEARANCE.get(str(appearance_id), "Unknown Type")


def parse_manufacturer_data(manufacturer_data):
    """Extract Manufacturer and Device Model ID from Manufacturer Data."""
    extracted_info = {}

    for key, value in manufacturer_data.items():
        _LOGGER.debug(f"🔍 Manufacturer Data Key: {key}, Type: {type(value)}, Value (repr): {repr(value)}")
        _LOGGER.debug(f"🔍 Manufacturer Data Hex [{key}]: {value.hex()}")

        manufacturer_id = int(key)  # Ensure it's an integer
        manufacturer = BLUETOOTH_SIG_COMPANIES.get(str(manufacturer_id), f"Unknown (ID {manufacturer_id})")

        if len(value) >= 4:
            device_model_id = int.from_bytes(value[2:4], "big")  # Extract bytes 3 & 4 as potential model ID
            device_type = get_device_type(device_model_id)
        else:
            device_model_id = "Unknown"
            device_type = "Unknown Type"

        extracted_info[manufacturer_id] = {
            "manufacturer": manufacturer,
            "device_model_id": device_model_id,
            "device_type": device_type,
        }

    return extracted_info


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

    manufacturer_data = service_info.manufacturer_data or {}
    _LOGGER.debug(f"🔍 Raw Manufacturer Data: {manufacturer_data}")

    extracted_info = parse_manufacturer_data(manufacturer_data)

    device_name = extract_friendly_name(service_info) or service_info.name or service_info.address
    manufacturer_id = next(iter(manufacturer_data), None)

    if manufacturer_id is not None and manufacturer_id in extracted_info:
        manufacturer = extracted_info[manufacturer_id]["manufacturer"]
        device_type = extracted_info[manufacturer_id]["device_type"]
    else:
        manufacturer = f"Unknown (ID {manufacturer_id})"
        device_type = "Unknown Type"

    if device_name == service_info.address:
        device_name = f"{manufacturer} Device ({service_info.address[-5:]})"
    
    _LOGGER.info(f"🆔 Discovered Device: {json.dumps(serialize_service_info(service_info), indent=2)}")
    
    return {
        "name": device_name,
        "manufacturer": manufacturer,
        "device_type": device_type,
        "mac_address": service_info.address,
        "rssi": service_info.rssi,
        "service_uuids": service_info.service_uuids,
    }


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the cache-clearing service in Home Assistant."""
    await fetch_bluetooth_database()
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

