"""Config flow for Proxmox Reboot Update."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_REBOOT_BUTTON, CONF_SOURCE_ENTITY, DOMAIN


class ProxmoxRebootUpdateConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for Proxmox Reboot Update."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle initial setup."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Proxmox Reboot Update",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="input_boolean")
                ),
                vol.Required(CONF_REBOOT_BUTTON): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="button")
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
