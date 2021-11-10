"""The cozytouch component."""
import asyncio
import logging
from datetime import timedelta

import voluptuous as vol
from cozytouchpy import CozytouchClient
from cozytouchpy.constant import DeviceType
from cozytouchpy.exception import AuthentificationFailed, CozytouchException
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_PASSWORD, CONF_TIMEOUT, CONF_USERNAME
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    PLATFORMS,
    CONF_COZYTOUCH_ACTUATOR,
    COORDINATOR,
    COZYTOUCH_ACTUATOR,
    COZYTOUCH_DATAS,
    DEFAULT_COZYTOUCH_ACTUATOR,
    DEFAULT_TIMEOUT,
    DOMAIN,
    HVAC_MODE_LIST,
    PRESET_MODE_LIST,
    SCHEMA_HEATER,
    SCHEMA_HEATINGCOOLINGZONE,
    SCHEMA_HEATINGZONE,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
                vol.Optional(
                    CONF_COZYTOUCH_ACTUATOR, default=DEFAULT_COZYTOUCH_ACTUATOR
                ): vol.In(SENSOR_TYPES),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup(hass, config):
    """Load configuration for Cozytouch component."""
    hass.data.setdefault(DOMAIN, {})

    if hass.config_entries.async_entries(DOMAIN) or DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
        )
    )

    return True


async def async_setup_entry(hass, config_entry):
    """Set up Cozytouch as config entry."""
    if not config_entry.options:
        hass.config_entries.async_update_entry(
            config_entry,
            options={
                "model": config_entry.data.get(
                    CONF_COZYTOUCH_ACTUATOR, DEFAULT_COZYTOUCH_ACTUATOR
                )
            },
        )

    async def async_fecth_datas():
        cozytouch = CozytouchClient(
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            config_entry.data[CONF_TIMEOUT],
        )
        try:
            await cozytouch.connect()
            return await cozytouch.get_setup()
        except AuthentificationFailed as error:
            _LOGGER.error("Authentification failed")
            raise AuthentificationFailed(error) from error
        except CozytouchException as error:
            _LOGGER.error("Cannot connect  to api")
            raise CozytouchException(error) from error

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_fecth_datas,
        update_interval=SCAN_INTERVAL,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = {
        COZYTOUCH_DATAS: coordinator.data,
        COORDINATOR: coordinator,
    }
    hass.data[DOMAIN][COZYTOUCH_ACTUATOR] = config_entry.options[
        CONF_COZYTOUCH_ACTUATOR
    ]

    device_registry = await dr.async_get_registry(hass)
    for gateway in coordinator.data.gateways.values():
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={
                (DOMAIN, gateway.data["placeOID"]),
                (DOMAIN, gateway.data["gatewayId"]),
            },
            manufacturer="Atlantic/Thermor",
            name="Cozytouch",
            sw_version=gateway.data["connectivity"]["protocolVersion"],
        )

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    if not config_entry.update_listeners:
        config_entry.add_update_listener(async_update_options)

    return True


async def async_update_options(hass, config_entry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return True


async def async_connect(config):
    """Connect to cozytouch."""
    cozytouch = CozytouchClient(
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
        config[CONF_TIMEOUT],
    )
    try:
        await cozytouch.connect()
        return await cozytouch.get_setup()
    except AuthentificationFailed as error:
        _LOGGER.error("Authentification failed")
        raise AuthentificationFailed from error
    except CozytouchException as error:
        _LOGGER.error("Cannot connect  to api")
        raise CozytouchException from error


class ClimateSchema:
    """Determine schema for a climate."""

    def __init__(self, model):
        """Get model."""
        self._model = model

    def hvac_list(self):
        """Return HVAC Mode List."""
        if DeviceType.HEATER == self._model:
            return SCHEMA_HEATER.get(HVAC_MODE_LIST)
        if DeviceType.APC_HEATING_ZONE == self._model:
            return SCHEMA_HEATINGZONE.get(HVAC_MODE_LIST)
        if DeviceType.APC_HEATING_COOLING_ZONE == self._model:
            return SCHEMA_HEATINGCOOLINGZONE.get(HVAC_MODE_LIST)

    def preset_list(self):
        """Return HVAC Mode List."""
        if DeviceType.HEATER == self._model:
            return SCHEMA_HEATER.get(PRESET_MODE_LIST)
        if DeviceType.APC_HEATING_ZONE == self._model:
            return SCHEMA_HEATINGZONE.get(PRESET_MODE_LIST)
        if DeviceType.APC_HEATING_COOLING_ZONE == self._model:
            return SCHEMA_HEATINGCOOLINGZONE.get(PRESET_MODE_LIST)
