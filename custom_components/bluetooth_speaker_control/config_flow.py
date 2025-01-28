from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_NAME
import bluetooth  # Using PyBluez for Bluetooth discovery

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=f"{user_input['device_name']} ({user_input['mac_address']})",
                data=user_input,
            )

        # Discover devices and store them
        self.devices = await self.hass.async_add_executor_job(self.discover_bluetooth_devices)

        if not self.devices:
            # If no devices are found, show an error
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_devices_found"}
            )

        # Display the configuration form with discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema()
        )

    def discover_bluetooth_devices(self):
        """Discover nearby Bluetooth devices."""
        try:
            devices = bluetooth.discover_devices(lookup_names=True)
            return [{"name": name, "mac": addr} for addr, name in devices]
        except Exception as e:
            self.hass.logger.error(f"Bluetooth discovery failed: {e}")
            return []

    @callback
    def _get_schema(self):
        """Generate the schema with discovered devices."""
        from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

        options = {
            f"{device['name']} ({device['mac']})": device['mac'] for device in self.devices
        }

        return {
            "device_name": SelectSelector(
                SelectSelectorConfig(
                    options=list(options.keys()),
                    mode="dropdown"
                )
            ),
            "mac_address": SelectSelector(
                SelectSelectorConfig(
                    options=list(options.values()),
                    mode="dropdown"
                )
            ),
        }
