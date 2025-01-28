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
        if user_input is not None:
            # Handle device selection
            selected_mac = user_input.get("device_mac")
            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                return await self.async_step_set_name()

            # Invalid device selection
            _LOGGER.error(f"Selected MAC address {selected_mac} not found in discovered devices.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(),
                errors={"base": "invalid_selection"},
            )

        # Attempt to discover devices
        #self.discovered_devices = await self._safe_discover_devices()
        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.warning("No Bluetooth devices discovered.")
            # No devices found: Display a static message
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(no_devices=True),
                errors={"base": "no_devices_found"},
            )

        # Show the list of discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user sets the nickname for the selected device."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=user_input["nickname"],
                data={
                    "nickname": user_input["nickname"],
                    "name": self.selected_device["name"],
                    "type": self.selected_device["type"],
                    "mac_address": self.selected_device["mac"],
                },
            )


        # Show form to set the nickname
        data_schema = vol.Schema(
            {
                vol.Required("nickname", default=self.selected_device["name"]): str,
            }
        )
        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
        )

    async def _safe_discover_devices(self):
        """Safely discover Bluetooth devices, logging any issues."""
        try:
            devices = await discover_bluetooth_devices(self.hass)
            _LOGGER.debug(f"Discovered devices: {devices}")
            return devices
        except Exception as e:
            _LOGGER.error(f"Error during Bluetooth device discovery: {e}")
            return []

    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate the schema for the list of devices."""
        if no_devices:
            # No devices found
            return vol.Schema({vol.Optional("device_mac"): vol.In({"none": "No devices found"})})

        # Devices found: Show list of devices with Type, Name, and MAC
        device_options = {
            device["mac"]: f"{device['type']} | {device['name']} ({device['mac']})"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required("device_mac"): vol.In(device_options),
            }
        )
