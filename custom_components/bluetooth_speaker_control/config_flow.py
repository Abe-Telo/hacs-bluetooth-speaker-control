from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
import logging
import asyncio
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None
        self.refresh_task = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list available devices with background refresh."""
        if user_input is not None:
            # Handle device selection
            selected_mac = user_input.get("device_mac")
            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                # Cancel the refresh task when proceeding
                if self.refresh_task:
                    self.refresh_task.cancel()
                return await self.async_step_set_name()

            # Invalid selection
            _LOGGER.error("Invalid device selection.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(),
                errors={"base": "invalid_selection"},
            )

        # Start the background refresh task
        if self.refresh_task is None:
            self.refresh_task = asyncio.create_task(self._refresh_devices())

        # Show the list of discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=user_input["device_name"],
                data={
                    "device_name": user_input["device_name"],
                    "mac_address": self.selected_device["mac"],
                },
            )

        # Display the form to set the device name
        data_schema = vol.Schema(
            {
                vol.Required(
                    "device_name", default=self.selected_device.get("name", "Unknown Device")
                ): str,
            }
        )

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
        )

    async def _refresh_devices(self):
        """Background task to refresh the list of Bluetooth devices every 10 seconds."""
        while True:
            try:
                _LOGGER.debug("Refreshing Bluetooth device list in the background.")
                self.discovered_devices = await discover_bluetooth_devices(self.hass)
                await asyncio.sleep(10)  # Wait for 15 seconds before the next refresh
            except asyncio.CancelledError:
                # Stop refreshing if the task is cancelled
                _LOGGER.debug("Background refresh task cancelled.")
                break
            except Exception as e:
                _LOGGER.error(f"Error during background device refresh: {e}")

    @callback
    def _get_device_schema(self):
        """Generate the schema for the list of devices."""
        device_options = {
            device["mac"]: f"{device['name']} ({device['mac']})" for device in self.discovered_devices
        }
        if not device_options:
            device_options["none"] = "No devices found"

        return vol.Schema(
            {
                vol.Required("device_mac"): vol.In(device_options),
            }
        )

    async def async_shutdown(self):
        """Stop the background refresh task when the flow ends."""
        if self.refresh_task:
            self.refresh_task.cancel()
            await self.refresh_task

