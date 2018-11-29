import logging
from datetime import timedelta

from cozypy.client import CozytouchClient
from cozypy.constant import DeviceType, DeviceState
from cozypy.exception import CozytouchException
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.util import Throttle

logger = logging.getLogger("cozytouch.binary_sensor")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    if "userId" not in config or "userPassword" not in config:
        raise CozytouchException("Bad configuration")
    client = CozytouchClient(config.get("userId"), config.get("userPassword"))
    setup = client.get_setup()
    devices = []
    for place in setup.places:
        for sensor in place.sensors:
            if sensor.widget == DeviceType.OCCUPANCY:
                devices.append(CozytouchOccupancySensor(sensor))


    logger.info("Found %d binary sensor" % len(devices))
    add_devices(devices)


class CozytouchOccupancySensor(BinarySensorDevice):

    def __init__(self, sensor):
        self.sensor = sensor

    @property
    def unique_id(self):
        return self.sensor.oid

    @property
    def name(self):
        return self.sensor.label

    @property
    def is_on(self):
        state = self.sensor.get_state(DeviceState.OCCUPANCY_STATE)
        if state is not None:
            if state == "noPersonInside":
                return False
            elif state == "PersonInside":
                return True
        return False

    @property
    def device_class(self):
        return "presence"

    @Throttle(timedelta(seconds=60))
    def update(self):
        logger.info("Update binary sensor %s" % self.sensor.label)

        self.sensor.update()


