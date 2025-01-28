from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_NAME

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bluetooth Speaker Control."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate user input here, if needed.
            return self.async_create_entry(
                title=user_input.get("name", DEFAULT_NAME),
                data=user_input,
            )

        # Show the setup form to the user.
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema()
        )

    @staticmethod
    @callback
    def _get_schema():
        """Return the schema for the setup form."""
        from homeassistant.helpers.selector import (
            TextSelector,
            TextSelectorConfig,
        )
        return {
            "name": TextSelector(TextSelectorConfig(type="text")),
        }
