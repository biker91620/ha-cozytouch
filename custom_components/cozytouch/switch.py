"""Switch for Cozytouch."""
import logging

from cozytouchpy import CozytouchException
from cozytouchpy.constant import DeviceType

from homeassistant.components.switch import SwitchEntity

from .const import CONF_COZYTOUCH_ACTUATOR, COZYTOUCH_DATAS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    datas = hass.data[DOMAIN][config_entry.entry_id][COZYTOUCH_DATAS]
    actuator = hass.data[DOMAIN][CONF_COZYTOUCH_ACTUATOR]
    devices = []
    for heater in datas.heaters:
        if actuator == "all":
            devices.append(CozytouchSwitch(heater))
        elif actuator == "pass" and heater.widget == DeviceType.PILOT_WIRE_INTERFACE:
            devices.append(CozytouchSwitch(heater))
        elif actuator == "i2g" and heater.widget == DeviceType.HEATER:
            devices.append(CozytouchSwitch(heater))
    async_add_entities(devices, True)


class CozytouchSwitch(SwitchEntity):
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
        return "{heater}".format(heater=self.heater.name)

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.heater.is_on

    @property
    def device_class(self):
        """Return the device class."""
        return "heat"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.heater.turn_on()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.heater.turn_off()

    async def async_update(self):
        """Fetch new state data for this heater."""
        _LOGGER.debug("Update switch %s", self.name)
        try:
            await self.heater.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve %s", self.name)

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": (DOMAIN, self.heater.data["placeOID"]),
        }
