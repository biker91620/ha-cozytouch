"""Binary sensors for Cozytouch."""
import logging

from cozytouchpy.constant import DeviceType

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN, COZYTOUCH_DATAS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""

    datas = hass.data[DOMAIN][config_entry.entry_id][COZYTOUCH_DATAS]

    devices = []
    for heater in datas.heaters:
        for sensor in [
            sensor for sensor in heater.sensors if sensor.widget == DeviceType.OCCUPANCY
        ]:
            devices.append(CozytouchOccupancySensor(sensor))

    _LOGGER.info("Found {count} binary sensor".format(count=len(devices)))
    async_add_entities(devices, True)


class CozytouchOccupancySensor(BinarySensorEntity):
    """Occupancy sensor (present/not present)."""

    def __init__(self, sensor):
        """Initialize occupancy sensor."""
        self.sensor = sensor

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
        await self.hass.async_add_executor_job(self.sensor.update)

    @property
    def device_info(self):
        """Return the device info."""

        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": {(DOMAIN, self.sensor.data["placeOID"])},
        }
