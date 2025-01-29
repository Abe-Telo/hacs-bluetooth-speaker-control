import logging
import voluptuous as vol
import asyncio
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_MAC_ADDRESS, CONF_NAME
from .bluetooth import discover_bluetooth_devices

_LOGGER = logging.getLogger(__name__)

SCAN_RETRY_DELAY = 5  # Retry scan delay in seconds
SCAN_MAX_RETRIES = 3  # Maximum retries for scanning


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the first step of the configuration flow."""
        errors = {}
        scan_attempts = 0

        while scan_attempts < SCAN_MAX_RETRIES:
            _LOGGER.info(f"🔍 Starting Bluetooth device discovery (attempt {scan_attempts + 1})")
            self.discovered_devices = await discover_bluetooth_devices(self.hass)

            if self.discovered_devices:
                _LOGGER.info(f"✅ Found {len(self.discovered_devices)} Bluetooth devices.")
                break  # Stop retrying if devices are found
            else:
                _LOGGER.warning(f"⚠️ No Bluetooth devices found. Retrying in {SCAN_RETRY_DELAY} seconds...")
                await asyncio.sleep(SCAN_RETRY_DELAY)
                scan_attempts += 1

        if user_input:
            selected_mac = user_input.get(CONF_MAC_ADDRESS)

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ Invalid selection: No device selected.")
                errors["base"] = "invalid_selection"
            else:
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

        if not self.discovered_devices:
            _LOGGER.warning("⚠️ No Bluetooth devices found after retries. Ensure devices are powered on and in range.")
            errors["base"] = "no_devices_found"

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(no_devices=not self.discovered_devices),
            errors=errors,
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input:
            _LOGGER.info(f"✅ Saving device with name: {user_input[CONF_NAME]}")
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=self.selected_device,
            )

        # Extract device details
        device_name = self.selected_device.get("name", "Unknown")
        device_mac = self.selected_device.get("mac", "Unknown")
        device_rssi = self.selected_device.get("rssi", "Unknown")
        device_uuids = self.selected_device.get("service_uuids", ["None"])

        # Format device details for display
        device_details = (
            f"**Device Information**\n\n"
            f"🔹 **Name:** {device_name}\n"
            f"🔹 **MAC Address:** `{device_mac}`\n"
            f"🔹 **RSSI:** `{device_rssi} dBm`\n"
            f"🔹 **Service UUIDs:** `{', '.join(device_uuids)}`\n"
        )

        _LOGGER.info(f"🔵 Device Details: {device_details}")

        # Define input schema
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=f"{device_name} ({device_mac})"): str,
            }
        )

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={"device_details": device_details},
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
            device["mac"]: f"{device['name']} ({device['mac']}) {device['rssi']} dBm"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_options),
            }
        )
