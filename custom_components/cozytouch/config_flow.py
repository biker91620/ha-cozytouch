"""Config flow to configure Cozytouch."""
import logging

import voluptuous as vol
from cozytouchpy import CozytouchClient
from cozytouchpy.exception import AuthentificationFailed, CozytouchException
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_TIMEOUT, CONF_USERNAME
from homeassistant.core import callback

from .const import (
    CONF_COZYTOUCH_ACTUATOR,
    DEFAULT_COZYTOUCH_ACTUATOR,
    DEFAULT_TIMEOUT,
    DOMAIN,
    SENSOR_TYPES,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
        vol.Optional(
            CONF_COZYTOUCH_ACTUATOR, default=DEFAULT_COZYTOUCH_ACTUATOR
        ): vol.In(SENSOR_TYPES),
    }
)

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class CozytouchFlowHandler(config_entries.ConfigFlow):
    """Handle a Cozytouch config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get option flow."""
        return CozytouchOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            try:
                cozytouch = CozytouchClient(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_TIMEOUT],
                )
                await cozytouch.connect()
            except AuthentificationFailed:
                errors = {"base": "login_inccorect"}
            except CozytouchException:
                errors = {"base": "parsing"}

            if "base" not in errors:
                return self.async_create_entry(title="Cozytouch", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CozytouchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry
        self._actuator = self.config_entry.options.get(
            CONF_COZYTOUCH_ACTUATOR, DEFAULT_COZYTOUCH_ACTUATOR
        )

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        options_schema = vol.Schema(
            {
                vol.Required(CONF_COZYTOUCH_ACTUATOR, default=self._actuator): vol.In(
                    SENSOR_TYPES
                )
            }
        )

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=options_schema)
