import logging
import asyncio
import requests
import json
import os
import codecs
import base64

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.components.bluetooth import (
    async_register_callback,
    async_discovered_service_info,
    BluetoothScanningMode,
    BluetoothChange,
)

_LOGGER = logging.getLogger(__name__)

CACHE_FILE = "manufacturer_cache.json"

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

MANUFACTURER_CACHE = {}

def decode_device_name(name_bytes):
    """Attempt to decode a device name from multiple encodings."""
    try:
        return name_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return name_bytes.decode("utf-16").strip()
        except UnicodeDecodeError:
            try:
                return name_bytes.decode("latin-1").strip()
            except UnicodeDecodeError:
                return base64.b64encode(name_bytes).decode()

def extract_friendly_name(service_info):
    """Extract a friendly name from available advertisement or manufacturer data."""
    if service_info.advertisement and hasattr(service_info.advertisement, "local_name"):
        return service_info.advertisement.local_name
    
    manufacturer_data = service_info.manufacturer_data
    if manufacturer_data:
        for key, value in manufacturer_data.items():
            hex_value = value.hex()
            byte_list = list(value)  # Convert to list of integers for manual analysis
            _LOGGER.debug(f"🔍 Raw Manufacturer Data [{key}]: {value} | Hex: {hex_value} | Bytes: {byte_list}")
            
            try:
                # Some devices prepend metadata before the name, so try extracting a substring
                possible_name = decode_device_name(value[2:])  # Skip first two bytes (potential metadata)
                if possible_name and all(32 <= ord(c) < 127 for c in possible_name):  # Ensure readable text
                    return possible_name
            except Exception as e:
                _LOGGER.debug(f"⚠️ Failed to decode manufacturer data key {key}: {e}")
                continue
    
    return None

def _format_device(service_info):
    """Extract relevant details from the discovered service info."""
    _LOGGER.debug(f"📡 Full Service Info as_dict(): {service_info.as_dict()}")
    
    device_name = extract_friendly_name(service_info) or service_info.name or service_info.address
    
    if isinstance(device_name, bytes):
        device_name = decode_device_name(device_name)
    
    manufacturer_data = service_info.manufacturer_data
    manufacturer_id = next(iter(manufacturer_data), None)
    manufacturer = BLUETOOTH_SIG_COMPANIES.get(manufacturer_id, f"Unknown (ID {manufacturer_id})")
    
    if device_name == service_info.address:
        device_name = f"{manufacturer} Device ({service_info.address[-5:]})"
    
    _LOGGER.info(f"🆔 Discovered Device: Name='{device_name}', Manufacturer='{manufacturer}', MAC='{service_info.address}'")
    
    return {
        "name": device_name,
        "manufacturer": manufacturer,
        "mac_address": service_info.address,
        "rssi": service_info.rssi,
        "service_uuids": service_info.service_uuids,
    }

async def scan_bluetooth_devices(hass):
    """Run both Active and Passive scans and merge results."""
    _LOGGER.debug("🔄 Running Active Scan...")
    active_results = await discover_bluetooth_devices(hass, timeout=10, passive_scanning=False)

    _LOGGER.debug("🔄 Running Passive Scan...")
    passive_results = await discover_bluetooth_devices(hass, timeout=10, passive_scanning=True)

    all_results = {device["mac"]: device for device in active_results + passive_results}
    _LOGGER.info(f"✅ Final Merged Bluetooth Devices: {list(all_results.values())}")

    return list(all_results.values())

async def discover_bluetooth_devices(hass, timeout=7, passive_scanning=True):
    """Discover Bluetooth devices using Home Assistant's built-in discovery API."""
    _LOGGER.debug(f"🔍 Discovering Bluetooth devices (Passive: {passive_scanning})...")
    discovered_devices = []

    for service_info in async_discovered_service_info(hass):
        _LOGGER.debug(f"📡 Service Info: {service_info}")
        discovered_devices.append(_format_device(service_info))

    if discovered_devices:
        _LOGGER.info(f"✅ Found {len(discovered_devices)} devices before scanning: {discovered_devices}")
        return discovered_devices

    def device_found(service_info, change: BluetoothChange):
        """Callback when a device is found in real-time."""
        device = _format_device(service_info)
        if device not in discovered_devices:
            discovered_devices.append(device)
            _LOGGER.debug(f"📡 Found Bluetooth device: {device}")

    try:
        _LOGGER.debug("📡 Registering Bluetooth scan callback...")
        scan_mode = BluetoothScanningMode.PASSIVE if passive_scanning else BluetoothScanningMode.ACTIVE
        stop_scan = async_register_callback(hass, device_found, match_dict={}, mode=scan_mode)
        _LOGGER.debug(f"⏳ Waiting {timeout} seconds for scan results...")
        await asyncio.sleep(timeout)
        _LOGGER.debug("🛑 Stopping Bluetooth scan...")
        hass.loop.call_soon_threadsafe(stop_scan)
    except Exception as e:
        _LOGGER.error(f"🔥 Error during Bluetooth scan: {e}")

    if not discovered_devices:
        _LOGGER.warning("⚠️ No Bluetooth devices found.")

    return discovered_devices

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the cache-clearing service in Home Assistant."""
    async def handle_clear_cache(call: ServiceCall) -> None:
        """Service call to clear the manufacturer cache."""
        _LOGGER.info("🗑️ Clearing manufacturer cache...")
        clear_manufacturer_cache()
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
