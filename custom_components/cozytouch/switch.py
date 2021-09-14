"""Switch for Cozytouch."""
import logging

from cozytouchpy.constant import DeviceType

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import CONF_COZYTOUCH_ACTUATOR, COORDINATOR, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    actuator = hass.data[DOMAIN][CONF_COZYTOUCH_ACTUATOR]
    devices = []
    for device in coordinator.data.devices.values():
        if actuator == "all":
            devices.append(CozytouchSwitch(device, coordinator))
        elif actuator == "pass" and device.widget == DeviceType.PILOT_WIRE_INTERFACE:
            devices.append(CozytouchSwitch(device, coordinator))
        elif actuator == "i2g" and device.widget == DeviceType.HEATER:
            devices.append(CozytouchSwitch(device, coordinator))
    async_add_entities(devices)


class CozytouchSwitch(CoordinatorEntity, SwitchEntity):
    """Header switch (on/off)."""

    def __init__(self, device, coordinator):
        """Initialize switch."""
        self.heater = device
        self.coordinator = coordinator

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
        return self.coordinator.data.devices[self.unique_id].is_on

    @property
    def device_class(self):
        """Return the device class."""
        return "heat"

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": (DOMAIN, self.heater.data["placeOID"]),
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.heater.turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.heater.turn_off()
        await self.coordinator.async_request_refresh()
