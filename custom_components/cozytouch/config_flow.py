"""Config flow to configure Cozytouch."""
import logging
import voluptuous as vol

from cozytouchpy import CozytouchClient

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TIMEOUT

from .const import DOMAIN, DEFAULT_TIMEOUT

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)

_LOGGER = logging.getLogger(__name__)


class CozytouchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Cozytouch config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the Cozytouch flow."""

        self.username = None
        self.password = None
        self.timeout = DEFAULT_TIMEOUT

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        errors = {}
        if user_input is not None:
            self.username = user_input[CONF_USERNAME]
            self.password = user_input[CONF_PASSWORD]

            try:
                client = CozytouchClient(self.username, self.password, self.timeout)
                setup = await client.async_get_setup()

                if setup:
                    return await self.async_step_register()
            except Exception:
                _LOGGER.info("Error Login {}".format(self.username))
                errors["base"] = "login_inccorect"

        # If there was no user input, do not show the errors.
        if user_input is None:
            errors = {}

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_register(self, user_input=None):
        """Step for register component."""

        errors = {}
        entry_id = self.hass.config_entries.async_entries(DOMAIN)
        self.bridge_id = "cozytouch_012345678"
        if self.bridge_id:
            if entry_id and entry_id.get("data", {}).get("id", 0) == self.bridge_id:
                self.hass.config_entries.async_remove(entry_id)
            return self.async_create_entry(
                title="Cozytouch",
                data={
                    "id": self.bridge_id,
                    CONF_USERNAME: self.username,
                    CONF_PASSWORD: self.password,
                    CONF_TIMEOUT: self.timeout,
                },
            )
        return self.async_show_form(step_id="register", errors=errors)
