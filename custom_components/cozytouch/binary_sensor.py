"""Binary sensors for Cozytouch."""
import logging
import voluptuous as vol
from cozypy.client import CozytouchClient
from cozypy.constant import DeviceType

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TIMEOUT, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
    """Setup the sensor platform."""

    # Assign configuration variables. The configuration check takes care they are
    # present.
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    timeout = config.get(CONF_TIMEOUT)

    # Setup cozytouch client
    client = CozytouchClient(username, password, timeout)
    setup = client.get_setup()
    devices = []
    for heater in setup.heaters:
        for sensor in [sensor for sensor in heater.sensors if sensor.widget == DeviceType.OCCUPANCY]:
            devices.append(CozytouchOccupancySensor(sensor))

    _LOGGER.info("Found {count} binary sensor".format(count=len(devices)))
    async_add_entities(devices, True)


class CozytouchOccupancySensor(BinarySensorDevice):
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
        return "{place} {sensor}".format(place=self.sensor.place.name, sensor=self.sensor.name)

    @property
    def is_on(self):
        """Return true if area is occupied."""
        return self.sensor.is_occupied

    @property
    def device_class(self):
        """Return the device class."""
        return "presence"

    def update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.info("Update binary sensor {name}".format(name=self.name))

        self.sensor.update()

    @property
    def device_info(self):
        """Return the device info."""

        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": (DOMAIN, "cozytouch"),
        }

