"""Binary sensors for Cozytouch."""
import logging

from cozytouchpy.constant import DeviceType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_WINDOW,
    DEVICE_CLASS_OCCUPANCY,
)

from .const import DOMAIN, COORDINATOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    devices = []
    for device in coordinator.data.devices.values():
        for sensor in device.sensors.values():
            if sensor.widget == DeviceType.OCCUPANCY:
                devices.append(CozytouchOccupancySensor(sensor, coordinator))
            elif sensor.widget == DeviceType.CONTACT:
                devices.append(CozytouchContactSensor(sensor, coordinator))

    async_add_entities(devices)


class CozytouchBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Generic Binarysensor."""

    def __init__(self, device, coordinator):
        """Initialize occupancy sensor."""
        self.sensor = device
        self.ref_id = self.sensor.parent.id
        self.ref_name = self.sensor.parent.name
        self.ref_manufacturer = self.sensor.parent.manufacturer
        self.coordinator = coordinator

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
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.ref_name,
            "identifiers": {(DOMAIN, self.ref_id)},
            "manufacturer": self.ref_manufacturer,
            "via_device": (DOMAIN, self.sensor.data["placeOID"]),
        }


class CozytouchOccupancySensor(CozytouchBinarySensor):
    """Occupancy sensor (present/not present)."""

    @property
    def is_on(self):
        """Return true if area is occupied."""
        return self.coordinator.data.devices[self.unique_id].is_occupied

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_OCCUPANCY


class CozytouchContactSensor(CozytouchBinarySensor):
    """Occupancy sensor (present/not present)."""

    @property
    def is_on(self):
        """Return true if contact is opened."""
        return self.coordinator.data.devices[self.unique_id].is_opened

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_WINDOW
