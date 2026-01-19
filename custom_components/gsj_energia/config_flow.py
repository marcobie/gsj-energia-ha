from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_DEVICE_ID, DEFAULT_PORT


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="GSJ Energia",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="localhost"): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_DEVICE_ID, default=414): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )
