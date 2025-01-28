from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_NAME
from .bluetooth import discover_bluetooth_devices
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, TextSelector, TextSelectorConfig
import logging

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list available devices with a refresh option."""
        if user_input is not None:
            # Proceed to the next step to configure the selected device
            selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == user_input["mac_address"]),
                None,
            )
            self.selected_device = selected_device
            return await self.async_step_set_name()

        # Discover devices using Home Assistant's Bluetooth integration
        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.error("No Bluetooth devices found during discovery.")
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_devices_found"},
                data_schema={},
                description_placeholders={"error": "No devices found. Please try refreshing."},
            )

        # Display the configuration form with discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
            description_placeholders={},
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user sets the name for the selected device."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=f"{user_input['device_name']} ({self.selected_device['mac']})",
                data={
                    "device_name": user_input["device_name"],
                    "mac_address": self.selected_device["mac"],
                },
            )

        # Pre-fill the MAC address for the selected device
        data_schema = {
            "device_name": TextSelector(TextSelectorConfig(type="text")),
            "mac_address": TextSelector(TextSelectorConfig(type="text")),
        }

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={
                "mac_address": self.selected_device["mac"],
            },
        )

    @callback
    def _get_schema(self):
        """Generate the schema with discovered devices."""
        options = {
            f"{device['name']} ({device['mac']})": device["mac"] for device in self.discovered_devices
        }

        return {
            "mac_address": SelectSelector(
                SelectSelectorConfig(
                    options=list(options.values()),
                    mode="dropdown"
                )
            )
        }
