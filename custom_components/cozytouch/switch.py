"""Switch for Cozytouch."""
import logging
import voluptuous as vol

from cozypy.constant import DeviceType
from cozypy.client import CozytouchClient

from homeassistant.components.switch import SwitchDevice
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM, CONF_TIMEOUT, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_COZYTOUCH_ACTUATOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
    """Setup the sensor platform."""

    # Assign configuration variables. The configuration check takes care they are
    # present.
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    timeout = config.get(CONF_TIMEOUT)
    actuator = CONF_COZYTOUCH_ACTUATOR

    # Setup cozytouch client
    client = CozytouchClient(username, password, timeout)
    setup = client.get_setup()
    devices = []

    for heater in setup.heaters:
        if actuator == "all":
            devices.append(CozytouchSwitch(heater))
        elif actuator == "pass" and heater.widget == DeviceType.HEATER_PASV:
            devices.append(CozytouchSwitch(heater))
        elif actuator == "i2g" and heater.widget == DeviceType.HEATER:
            devices.append(CozytouchSwitch(heater))

    _LOGGER.info("Found {count} switch".format(count=len(devices)))
    add_devices(devices)


class CozytouchSwitch(SwitchDevice):
    """Header switch (on/off)."""

    def __init__(self, heater):
        """Initialize switch."""
        self.heater = heater

    @property
    def unique_id(self):
        """Return the unique id of this switch."""
        return self.heater.id

    @property
    def name(self):
        """Return the display name of this switch."""
        return "{place} {heater}".format(place=self.heater.place.name, heater=self.heater.name)

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.heater.is_on

    @property
    def device_class(self):
        """Return the device class."""
        return "heat"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.heater.turn_on()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self.heater.turn_off()

    def update(self):
        """Fetch new state data for this heater."""
        _LOGGER.info("Update switch {name}".format(name=self.name))

        self.heater.update()

    @property
    def device_info(self):
        """Return the device info."""

        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": (DOMAIN, "cozytouch"),
        }
