"""Config flow for Inseego M3000 Hotspot integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=300)
        ),
    }
)


async def validate_connection(hass: HomeAssistant, host: str) -> dict[str, Any]:
    """Validate the connection to the Inseego M3000."""
    session = async_get_clientsession(hass)
    url = f"http://{host}/srv/status"
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as response:
            if response.status != 200:
                raise ConnectionError(f"HTTP {response.status}")
            
            data = await response.json()
            
            # Validate that this is indeed an Inseego M3000
            if "statusData" not in data:
                raise ValueError("Invalid response format")
            
            status_data = data.get("statusData", {})
            device_info = {
                "network": status_data.get("statusBarNetwork", "Unknown"),
                "technology": status_data.get("statusBarTechnology", "Unknown"),
            }
            
            return device_info
            
    except aiohttp.ClientError as err:
        _LOGGER.error("Connection error: %s", err)
        raise ConnectionError(f"Cannot connect to device: {err}")
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise


class InseegoM3000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inseego M3000 Hotspot."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                device_info = await validate_connection(self.hass, user_input[CONF_HOST])
                
                # Create a unique ID based on the host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Inseego M3000 ({user_input[CONF_HOST]})",
                    data=user_input,
                )
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_device"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
