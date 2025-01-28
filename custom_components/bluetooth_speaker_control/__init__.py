from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from .bluetooth import discover_bluetooth_devices, pair_device, connect_device, disconnect_device
import logging

DOMAIN = "bluetooth_speaker_control"
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Bluetooth Speaker Control integration."""
    _LOGGER.info("🔵 Initializing Bluetooth Speaker Control integration")

    async def handle_pair_speaker(call: ServiceCall):
        """Handle pairing a Bluetooth speaker."""
        mac_address = call.data.get("mac_address")
        if not mac_address:
            _LOGGER.error("❌ Pairing failed: No MAC address provided")
            return
        
        success = pair_device(mac_address)
        status = f"✅ Paired with {mac_address}" if success else f"❌ Pairing failed for {mac_address}"
        _LOGGER.info(status)
        hass.states.async_set(f"{DOMAIN}.pair_status", status)

    async def handle_connect_speaker(call: ServiceCall):
        """Handle connecting to a Bluetooth speaker."""
        mac_address = call.data.get("mac_address")
        if not mac_address:
            _LOGGER.error("❌ Connection failed: No MAC address provided")
            return
        
        success = connect_device(mac_address)
        status = f"✅ Connected to {mac_address}" if success else f"❌ Connection failed for {mac_address}"
        _LOGGER.info(status)
        hass.states.async_set(f"{DOMAIN}.connect_status", status)

    async def handle_disconnect_speaker(call: ServiceCall):
        """Handle disconnecting from a Bluetooth speaker."""
        mac_address = call.data.get("mac_address")
        if not mac_address:
            _LOGGER.error("❌ Disconnection failed: No MAC address provided")
            return
        
        success = disconnect_device(mac_address)
        status = f"✅ Disconnected from {mac_address}" if success else f"❌ Disconnection failed for {mac_address}"
        _LOGGER.info(status)
        hass.states.async_set(f"{DOMAIN}.disconnect_status", status)

    async def handle_scan_devices(call: ServiceCall):
        """Handle scanning for Bluetooth devices."""
        _LOGGER.info("🔍 Scanning for Bluetooth devices...")
        devices = await discover_bluetooth_devices(hass)
        if not devices:
            _LOGGER.warning("⚠️ No Bluetooth devices found during scan.")
        else:
            _LOGGER.info(f"✅ Found {len(devices)} Bluetooth devices.")
            for device in devices:
                _LOGGER.info(f"📡 Discovered: {device}")

        hass.states.async_set(f"{DOMAIN}.scan_status", f"Scanned {len(devices)} devices")

    # Register services
    hass.services.async_register(DOMAIN, "pair_speaker", handle_pair_speaker)
    hass.services.async_register(DOMAIN, "connect_speaker", handle_connect_speaker)
    hass.services.async_register(DOMAIN, "disconnect_speaker", handle_disconnect_speaker)
    hass.services.async_register(DOMAIN, "scan_devices", handle_scan_devices)

    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up the integration from a config entry."""
    _LOGGER.info("🔵 Setting up Bluetooth Speaker Control from entry")
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    _LOGGER.info("🔵 Unloading Bluetooth Speaker Control entry")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
