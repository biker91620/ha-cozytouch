import logging
import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM, CONF_TIMEOUT
import homeassistant.helpers.config_validation as cv

from custom_components.cozytouch import COZYTOUCH_CLIENT_REQUIREMENT

_LOGGER = logging.getLogger(__name__)

# Requires cozytouch client library.
REQUIREMENTS = [COZYTOUCH_CLIENT_REQUIREMENT]


DEFAULT_TIMEOUT = 10

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    from cozypy.client import CozytouchClient
    from cozypy.constant import DeviceType

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

    _LOGGER.info("Found %d binary sensor" % len(devices))
    add_devices(devices)


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
        return "%s %s" % (self.sensor.place.name, self.sensor.name)

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
        _LOGGER.info("Update binary sensor %s" % self.name)

        self.sensor.update()


