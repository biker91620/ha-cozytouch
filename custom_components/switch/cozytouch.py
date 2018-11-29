import logging
from datetime import timedelta

from homeassistant.components.switch import SwitchDevice

from cozypy.client import CozytouchClient
from cozypy.exception import CozytouchException
from cozypy.constant import DeviceState
from homeassistant.util import Throttle

logger = logging.getLogger("cozytouch.switch")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    if "userId" not in config or "userPassword" not in config:
        raise CozytouchException("Bad configuration")
    client = CozytouchClient(config.get("userId"), config.get("userPassword"))
    setup = client.get_setup()
    devices = []
    for place in setup.places:
        for heater in place.heaters:
            devices.append(CozytouchSwitch(heater))

    logger.info("Found %d switch" % len(devices))
    add_devices(devices)


class CozytouchSwitch(SwitchDevice):

    def __init__(self, heater):
        self.heater = heater

    @property
    def unique_id(self):
        return self.heater.oid

    @property
    def name(self):
        return self.heater.label

    @property
    def is_on(self):
        return self.heater.get_state(DeviceState.ON_OFF_STATE)

    @property
    def device_class(self):
        return "heat"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        pass

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        pass

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        pass

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        pass

    @Throttle(timedelta(seconds=60))
    def update(self):
        logger.info("Update switch %s" % self.heater.label)

        self.heater.update()
