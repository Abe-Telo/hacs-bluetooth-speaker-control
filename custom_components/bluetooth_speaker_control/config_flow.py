import logging
import voluptuous as vol
import asyncio
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_MAC_ADDRESS, CONF_NAME
from .bluetooth import discover_bluetooth_devices

_LOGGER = logging.getLogger(__name__)

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the first step of the configuration flow."""
        errors = {}

        try:
            _LOGGER.info("🔍 Starting Bluetooth device discovery (config_flow).")

            # Introduce a delay before scanning to improve results
            _LOGGER.info("⏳ Waiting 5 seconds before scanning...")
            await asyncio.sleep(5)

            self.discovered_devices = await discover_bluetooth_devices(self.hass)

            if not self.discovered_devices:
                _LOGGER.warning("⚠️ No Bluetooth devices found. Retrying scan in 5 seconds...")
                await asyncio.sleep(5)
                self.discovered_devices = await discover_bluetooth_devices(self.hass)

            if not self.discovered_devices:
                _LOGGER.error("❌ No Bluetooth devices found after retry.")
                errors["base"] = "no_devices_found"

        except Exception as e:
            _LOGGER.error(f"🔥 Error during device discovery: {e}", exc_info=True)
            errors["base"] = "discovery_failed"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(no_devices=True),
                errors=errors,
            )

        if user_input:
            selected_mac = user_input.get(CONF_MAC_ADDRESS)

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ Invalid selection: No device selected.")
                errors["base"] = "invalid_selection"
            else:
                # Find selected device
                self.selected_device = next(
                    (device for device in self.discovered_devices if device["mac"] == selected_mac),
                    None,
                )
                if self.selected_device:
                    _LOGGER.info(f"🟢 Selected Bluetooth Device: {self.selected_device}")
                    return await self.async_step_set_name()
                else:
                    _LOGGER.error(f"❌ Selected MAC address {selected_mac} not found in discovered devices.")
                    errors["base"] = "device_not_found"

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
            errors=errors,
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if not self.selected_device:
            _LOGGER.error("❌ No selected device found. Restarting flow.")
            return await self.async_step_user()

        if user_input:
            _LOGGER.info(f"✅ Saving device with nickname: {user_input[CONF_NAME]}")

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=self.selected_device,
            )

        device_name = self.selected_device.get("name", "Unknown")
        device_mac = self.selected_device.get("mac", "Unknown")

        default_nickname = f"{device_name} ({device_mac})"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=default_nickname): str,
            }
        )

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
        )

    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate the schema for the list of devices."""
        if no_devices:
            return vol.Schema(
                {
                    vol.Optional(CONF_MAC_ADDRESS): vol.In(
                        {"none": "No devices found. Ensure devices are discoverable and try again."}
                    )
                }
            )

        device_options = {
            device["mac"]: f"{device['name']} ({device['mac']})"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_options),
            }
        )
