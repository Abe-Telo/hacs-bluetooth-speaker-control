import logging
import voluptuous as vol
import asyncio
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_MAC_ADDRESS, CONF_NAME
from .bluetooth import discover_bluetooth_devices

_LOGGER = logging.getLogger(__name__)

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Bluetooth Speaker Control configuration flow."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Step to scan for Bluetooth devices and allow selection."""
        errors = {}

        _LOGGER.info("🔍 Starting Bluetooth discovery in config flow...")

        for attempt in range(3):  # Retry scanning up to 3 times if needed
            _LOGGER.info(f"🕵️‍♂️ Scan attempt {attempt + 1}...")
            try:
                self.discovered_devices = await discover_bluetooth_devices(self.hass, timeout=5)
                if self.discovered_devices:
                    _LOGGER.info(f"✅ Found {len(self.discovered_devices)} devices!")
                    break  # Exit loop if devices are found
            except Exception as e:
                _LOGGER.error(f"🔥 Bluetooth scan error: {e}")
                errors["base"] = "scan_failed"

            await asyncio.sleep(2)  # Short delay before retrying

        if user_input:
            selected_mac = user_input.get(CONF_MAC_ADDRESS)

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ No device selected.")
                errors["base"] = "invalid_selection"
            else:
                self.selected_device = next(
                    (device for device in self.discovered_devices if device["mac"] == selected_mac),
                    None,
                )
                if self.selected_device:
                    _LOGGER.info(f"🟢 Selected device: {self.selected_device}")
                    return await self.async_step_set_name()
                else:
                    _LOGGER.error(f"❌ Selected MAC {selected_mac} not found in scan results.")
                    errors["base"] = "device_not_found"

        if not self.discovered_devices:
            _LOGGER.warning("⚠️ No Bluetooth devices discovered.")
            errors["base"] = "no_devices_found"

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(no_devices=not self.discovered_devices),
            errors=errors,
        )

    async def async_step_set_name(self, user_input=None):
        """Step to set the name for the selected device."""
        if user_input:
            _LOGGER.info(f"✅ Saving device with name: {user_input[CONF_NAME]}")
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=self.selected_device,
            )

        device_name = self.selected_device.get("name", "Unknown")
        device_mac = self.selected_device.get("mac", "Unknown")

        return self.async_show_form(
            step_id="set_name",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=f"{device_name} ({device_mac})"): str,
                }
            ),
        )

    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate the schema for discovered devices."""
        if no_devices:
            return vol.Schema(
                {
                    vol.Optional(CONF_MAC_ADDRESS): vol.In(
                        {"none": "No devices found. Ensure devices are discoverable and try again."}
                    )
                }
            )

        device_options = {
            device["mac"]: f"{device['name']} ({device['mac']}) | RSSI: {device['rssi']} dBm"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_options),
            }
        )
