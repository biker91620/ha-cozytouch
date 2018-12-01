import logging
from datetime import timedelta

from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from cozypy.client import CozytouchClient
from cozypy.exception import CozytouchException
from cozypy.constant import DeviceType, DeviceState
from homeassistant.util import Throttle

logger = logging.getLogger("cozytouch.sensor")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    if "userId" not in config or "userPassword" not in config:
        raise CozytouchException("Bad configuration")
    client = CozytouchClient(config.get("userId"), config.get("userPassword"))
    setup = client.get_setup()
    devices = []
    for heater in setup.heaters:
        for sensor in heater.sensors:
            if sensor.widget == DeviceType.TEMPERATURE:
                devices.append(CozyTouchTemperatureSensor(sensor))

    logger.info("Found %d sensor" % len(devices))

    add_devices(devices)


class CozyTouchTemperatureSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, sensor):
        """Initialize the sensor."""
        self.sensor = sensor

    @property
    def unique_id(self):
        return self.sensor.id

    @property
    def name(self):
        """Return the name of the sensor."""
        return "%s %s" % (self.sensor.place.name, self.sensor.name)

    @property
    def state(self):
        return self.sensor.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


    @Throttle(timedelta(seconds=60))
    def update(self):
        logger.info("Update sensor %s" % self.name)

        self.sensor.update()

