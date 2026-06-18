"""Config flow for Inseego M3000 Hotspot integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN
from .coordinator import _build_bcrypt_salt, _hash_password

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
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

            if "statusData" not in data:
                raise ValueError("Invalid response format")

            status_data = data.get("statusData", {})
            return {
                "network": status_data.get("statusBarNetwork", "Unknown"),
                "technology": status_data.get("statusBarTechnology", "Unknown"),
            }

    except aiohttp.ClientError as err:
        _LOGGER.error("Connection error: %s", err)
        raise ConnectionError(f"Cannot connect to device: {err}")
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise


async def validate_auth(hass: HomeAssistant, host: str, password: str) -> None:
    """Validate device password by attempting the login flow."""
    session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
    try:
        # Get login token
        async with session.get(
            f"http://{host}/login",
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
        ) as resp:
            html = await resp.text()

        import re
        match = re.search(r'<input[^>]+id="gSecureToken"[^>]+value="([^"]+)"', html)
        if not match:
            match = re.search(r'<input[^>]+value="([^"]+)"[^>]+id="gSecureToken"', html)
        if not match:
            raise ValueError("Login token not found on device login page")
        token = match.group(1)

        # Hash password and submit
        salt = _build_bcrypt_salt(token)
        password_hash = await hass.async_add_executor_job(_hash_password, password, salt)

        async with session.post(
            f"http://{host}/submitLogin/",
            data={"shaPassword": password_hash.decode(), "gSecureToken": token},
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                raise PermissionError(f"Login rejected: HTTP {resp.status}")

        # Verify session is valid
        async with session.get(
            f"http://{host}/rest/1.0/DeviceInfo",
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
        ) as resp:
            if resp.status == 401:
                raise PermissionError("Invalid password")

    finally:
        await session.close()


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
                await validate_connection(self.hass, user_input[CONF_HOST])

                if password := user_input.get(CONF_PASSWORD):
                    await validate_auth(self.hass, user_input[CONF_HOST], password)

                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Inseego M3000 ({user_input[CONF_HOST]})",
                    data=user_input,
                )
            except config_entries.data_entry_flow.AbortFlow:
                raise
            except PermissionError:
                errors[CONF_PASSWORD] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_device"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
