from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list available devices."""
        errors = {}

        _LOGGER.info("🔍 Starting Bluetooth device discovery...")

        if user_input is not None:
            selected_mac = user_input.get("device_mac")

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ Invalid selection: No device selected.")
                errors["base"] = "invalid_selection"
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_device_schema(no_devices=not self.discovered_devices),
                    errors=errors,
                )

            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )

            if self.selected_device:
                _LOGGER.info(f"🟢 Selected Bluetooth Device: {self.selected_device}")
                return await self.async_step_set_name()

            _LOGGER.error(f"❌ Selected MAC address {selected_mac} not found in discovered devices.")
            errors["base"] = "device_not_found"

        try:
            devices = await discover_bluetooth_devices(self.hass)
            self.discovered_devices = devices
        except Exception as e:
            _LOGGER.error(f"🔥 Error during device discovery: {e}")
            errors["base"] = "discovery_failed"

        if not self.discovered_devices:
            _LOGGER.warning(
                "⚠️ No devices discovered. Ensure devices are powered on, discoverable, and within range."
            )
            errors["base"] = "no_devices_found"

        _LOGGER.info(f"✅ Discovered {len(self.discovered_devices)} devices.")
        for device in self.discovered_devices:
            _LOGGER.debug(f"🔵 Discovered Device: {device}")

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(no_devices=not self.discovered_devices),
            errors=errors,
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input is not None:
            _LOGGER.info(f"✅ Saving device with nickname: {user_input['nickname']}")
            return self.async_create_entry(
                title=user_input["nickname"],
                data=self.selected_device,
            )

        # Extract relevant device information
        device_name = self.selected_device.get("name", "Unknown")
        device_mac = self.selected_device.get("mac", "Unknown")
        default_nickname = f"{device_name} ({device_mac})"

        # Define input schema
        data_schema = vol.Schema(
            {
                vol.Required("nickname", default=default_nickname): str,
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
                    vol.Optional("device_mac"): vol.In(
                        {"none": "No devices found. Make sure devices are discoverable and try again."}
                    )
                }
            )

        device_options = {
            device["mac"]: f"{device['name']} ({device['mac']})"
            for device in self.discovered_devices
        }

        return vol.Schema(
          
