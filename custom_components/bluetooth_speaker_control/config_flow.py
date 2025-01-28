from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, TextSelector, TextSelectorConfig
import logging

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
            # User has selected a device; proceed to the naming step
            selected_mac = user_input.get("mac_address")
            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                return await self.async_step_set_name()

            # Invalid selection, return error
            _LOGGER.error("Invalid selection. Device not found.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_schema(),
                errors={"base": "invalid_selection"},
            )

        # Discover devices using Home Assistant's Bluetooth integration
        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.warning("No Bluetooth devices found.")
            # Show an empty schema with a "no devices found" error
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_schema(no_devices=True),
                errors={"base": "no_devices_found"},
            )

        # Display the configuration form with discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user sets the name for the selected device."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=user_input["device_name"],
                data={
                    "device_name": user_input["device_name"],
                    "mac_address": self.selected_device["mac"],
                },
            )

        # Display form for entering the name
        data_schema = {
            "device_name": TextSelector(TextSelectorConfig(type="text")),
        }

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={
                "mac_address": self.selected_device["mac"],
            },
        )

    @callback
    def _get_schema(self, no_devices=False):
        """Generate the schema for the user step."""
        if no_devices:
            # No devices found: Show a static "refresh" option
            return {
                "mac_address": TextSelector(
                    TextSelectorConfig(
                        type="text",
                        default="No devices found. Please refresh.",
                    )
                )
            }

        # Devices found: Show a dropdown with options
        options = {
            device["mac"]: f"{device['name']} ({device['mac']})" for device in self.discovered_devices
        }

        return {
            "mac_address": SelectSelector(
                SelectSelectorConfig(
                    options=[{"value": k, "label": v} for k, v in options.items()],
                    mode="dropdown",
                )
            )
        }
