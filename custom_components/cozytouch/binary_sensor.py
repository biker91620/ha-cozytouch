"""Binary sensors for Cozytouch."""
import logging

from cozytouchpy import CozytouchException
from cozytouchpy.constant import DeviceType

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import COZYTOUCH_DATAS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    datas = hass.data[DOMAIN][config_entry.entry_id][COZYTOUCH_DATAS]

    devices = []
    for heater in datas.heaters:
        for sensor in [
            sensor for sensor in heater.sensors if sensor.widget == DeviceType.OCCUPANCY
        ]:
            devices.append(CozytouchOccupancySensor(sensor, heater))

    _LOGGER.info("Found {count} binary sensor".format(count=len(devices)))
    async_add_entities(devices, True)


class CozytouchOccupancySensor(BinarySensorEntity):
    """Occupancy sensor (present/not present)."""

    def __init__(self, sensor, device):
        """Initialize occupancy sensor."""
        self.sensor = sensor
        self.ref_id = device.id
        self.ref_name = device.name
        self.ref_manufacturer = device.manufacturer

    @property
    def unique_id(self):
        """Return the unique id of this switch."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this switch."""
        return "{place} {sensor}".format(
            place=self.sensor.place.name, sensor=self.sensor.name
        )

    @property
    def is_on(self):
        """Return true if area is occupied."""
        return self.sensor.is_occupied

    @property
    def device_class(self):
        """Return the device class."""
        return "presence"

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update binary sensor {name}".format(name=self.name))
        try:
            await self.sensor.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve {}".format(self.name))

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.ref_name,
            "identifiers": {(DOMAIN, self.ref_id)},
            "manufacturer": self.ref_manufacturer,
            "via_device": (DOMAIN, self.sensor.data["placeOID"]),
        }
