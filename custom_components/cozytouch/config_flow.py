"""Config flow to configure Cozytouch."""
import voluptuous as vol
import cozypy
from cozypy.exception import CozytouchException

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

DEFAULT_TIMEOUT = 10
DOMAIN = "cozytouch"

class CozytouchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Cozytouch config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the Cozytouch flow."""

        self.username = None
        self.password = None

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        errors = {}
        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        if user_input is not None:
            self.username = user_input["username"]
            self.password = user_input["password"]

            try:
                client = CozytouchClient(username, password, timeout)
                setup = client.get_setup()
               
            except CozytouchException:
                errors["base"] = "login_inccorect"

        # If there was no user input, do not show the errors.
        if user_input is None:
            errors = {}

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_register(self, user_input=None):
        """Step for register component."""

        errors = {}
        entry_id = self.hass.config_entries.async_entries(DOMAIN)
        self.box_id = "cozytouch_012345678"
        if self.box_id:
            if entry_id and entry_id.get("data", {}).get("id", 0) == self.box_id:
                self.hass.config_entries.async_remove(entry_id)
            return self.async_create_entry(
                title=f"{TEMPLATE_SENSOR}",
                data={
                    "id": self.box_id,
                    "username": self.username,
                    "password": self.password,
                },
            )
        return self.async_show_form(step_id="register", errors=errors)
