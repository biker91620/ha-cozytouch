"""The cozytouch component."""
import asyncio
import logging

import voluptuous as vol

from cozytouchpy.exception import AuthentificationFailed, CozytouchException
from cozytouchpy import CozytouchClient

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_PASSWORD, CONF_TIMEOUT, CONF_USERNAME
from homeassistant.helpers import device_registry as dr

from .const import COMPONENTS, COZYTOUCH_DATAS, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


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
    try:
        setup = await async_connect(hass, config_entry.data)
        if setup is None:
            return False
    except CozytouchException:
        return False

    hass.data[DOMAIN][config_entry.entry_id] = {COZYTOUCH_DATAS: setup}

    device_registry = await dr.async_get_registry(hass)
    for gateway in setup.data.get("gateways"):
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, gateway["placeOID"]), (DOMAIN, gateway["gatewayId"])},
            manufacturer="Atlantic/Thermor",
            name="Cozytouch",
            sw_version=gateway["connectivity"]["protocolVersion"],
        )

    for component in COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in COMPONENTS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return True


async def async_connect(hass, parameters):
    """Connect to cozytouch."""
    try:
        cozytouch = CozytouchClient(
            parameters[CONF_USERNAME],
            parameters[CONF_PASSWORD],
            parameters[CONF_TIMEOUT],
        )
        await cozytouch.connect()
        return await cozytouch.get_setup()
    except AuthentificationFailed as e:
        raise AuthentificationFailed(e)
    except CozytouchException as e:
        raise CozytouchException(e)
