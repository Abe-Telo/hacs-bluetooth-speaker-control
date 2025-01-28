from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for the Bluetooth Speaker Control integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate user input and save the configuration
            return self.async_create_entry(
                title="Bluetooth Speaker Control",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_user_input_schema()
        )

    @staticmethod
    @callback
    def _get_user_input_schema():
        """Return the input schema for the configuration flow."""
        from homeassistant.helpers.selector import TextSelector

        return {
            "name": TextSelector({"type": "text"}),
        }
