import logging
import voluptuous as vol

from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM, CONF_TIMEOUT
from homeassistant.helpers import config_validation as cv

from custom_components.cozytouch import COZYTOUCH_CLIENT_REQUIREMENT

_LOGGER = logging.getLogger(__name__)

# Requires cozytouch client library.
REQUIREMENTS = [COZYTOUCH_CLIENT_REQUIREMENT]

DEFAULT_TIMEOUT = 10
KW_UNIT = 'kW'

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
        for sensor in heater.sensors:
            if sensor.widget == DeviceType.TEMPERATURE:
                devices.append(CozyTouchTemperatureSensor(sensor))
            elif sensor.widget == DeviceType.ELECTRECITY:
                devices.append(CozyTouchElectricitySensor(sensor))

    _LOGGER.info("Found %d switch" % len(devices))
    add_devices(devices)


class CozyTouchTemperatureSensor(Entity):
    """Representation of a temperature sensor."""

    def __init__(self, sensor):
        """Initialize temperature sensor."""
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
    def state(self):
        """ Return the temperature """
        return self.sensor.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


    def update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.info("Update sensor %s" % self.name)

        self.sensor.update()


class CozyTouchElectricitySensor(Entity):
    """Representation of an electricity Sensor."""

    def __init__(self, sensor):
        """Initialize the sensor."""
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
    def state(self):
        """Return the electricity consumption."""
        return self.sensor.consumption / 1000

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return KW_UNIT


    def update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.info("Update sensor %s" % self.name)

        self.sensor.update()

