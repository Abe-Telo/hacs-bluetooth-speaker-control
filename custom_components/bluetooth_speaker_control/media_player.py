from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)

class BluetoothSpeaker(MediaPlayerEntity):
    """Representation of a Bluetooth speaker."""

    def __init__(self, name, speaker_mac):
        self._name = name
        self._speaker_mac = speaker_mac
        self._state = "idle"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def supported_features(self):
        return (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
        )

    async def async_turn_on(self):
        """Connect to the speaker."""
        # Add connection logic here
        self._state = "playing"

    async def async_turn_off(self):
        """Disconnect from the speaker."""
        # Add disconnection logic here
        self._state = "off"
