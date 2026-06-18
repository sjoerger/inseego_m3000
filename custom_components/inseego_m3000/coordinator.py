"""DataUpdateCoordinator for Inseego M3000."""
from __future__ import annotations

import base64
import logging
import re
from datetime import timedelta

import aiohttp
import bcrypt

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Bcrypt uses the same bit layout as standard base64 but a different alphabet.
# Translating after standard base64 encode produces an identical result to the
# FFI encode_base64() call the library uses.
_STD_B64    = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_BCRYPT_B64 = "./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_B64_TRANS  = str.maketrans(_STD_B64, _BCRYPT_B64)


def _build_bcrypt_salt(token: str) -> bytes:
    """Build the bcrypt salt from the device login token."""
    encoded = base64.b64encode(token[:16].encode()).decode().rstrip("=").translate(_B64_TRANS)
    return f"$2a$10${encoded}".encode()


def _hash_password(password: str, salt: bytes) -> bytes:
    """Hash password with bcrypt (CPU-bound — run in executor)."""
    return bcrypt.hashpw(password.encode(), salt)


class InseegoM3000DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Inseego M3000 data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.host = entry.data[CONF_HOST]
        self._password: str | None = entry.data.get(CONF_PASSWORD)
        self._auth_session: aiohttp.ClientSession | None = None
        self._action_token: str | None = None
        self._authenticated = False

        # Shared HA session for unauthenticated endpoints
        self.session = async_get_clientsession(hass)

        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    @property
    def _has_auth(self) -> bool:
        return bool(self._password)

    async def close(self) -> None:
        """Close the authenticated session on integration unload."""
        if self._auth_session:
            await self._auth_session.close()
            self._auth_session = None

    # -------------------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------------------

    async def _ensure_authenticated(self) -> None:
        if not self._authenticated or self._auth_session is None:
            await self._authenticate()

    async def _authenticate(self) -> None:
        """Run the full bcrypt login flow."""
        if self._auth_session:
            await self._auth_session.close()
        # Must use a real cookie jar — HA's shared session uses DummyCookieJar
        self._auth_session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        )
        try:
            token = await self._get_login_token()
            salt = _build_bcrypt_salt(token)
            password_hash = await self.hass.async_add_executor_job(
                _hash_password, self._password, salt
            )
            await self._submit_login(token, password_hash)
            self._action_token = await self._get_action_token()
            self._authenticated = True
            _LOGGER.debug("Authentication successful")
        except Exception:
            self._authenticated = False
            raise

    async def _get_login_token(self) -> str:
        """Extract gSecureToken from the device login page HTML."""
        url = f"http://{self.host}/login"
        async with self._auth_session.get(
            url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        ) as resp:
            if "401lockedout" in str(resp.url):
                raise UpdateFailed("Device is locked out — wait for lockout to expire or reboot")
            html = await resp.text()

        match = re.search(r'<input[^>]+id="gSecureToken"[^>]+value="([^"]+)"', html)
        if not match:
            match = re.search(r'<input[^>]+value="([^"]+)"[^>]+id="gSecureToken"', html)
        if not match:
            raise UpdateFailed("Login token not found on device login page")
        return match.group(1)

    async def _submit_login(self, token: str, password_hash: bytes) -> None:
        """POST credentials to the device."""
        url = f"http://{self.host}/submitLogin/"
        async with self._auth_session.post(
            url,
            data={"shaPassword": password_hash.decode(), "gSecureToken": token},
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"Login failed: HTTP {resp.status} — check password")

    async def _get_action_token(self) -> str | None:
        """Fetch gSecureToken from usageinfo for future control operations."""
        url = f"http://{self.host}/apps_home/usageinfo"
        async with self._auth_session.get(
            url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        ) as resp:
            if "401lockedout" in str(resp.url) or resp.status != 200:
                return None
            try:
                data = await resp.json(content_type=None)
                return data.get("gSecureToken")
            except Exception:
                return None

    # -------------------------------------------------------------------------
    # Authenticated REST helper
    # -------------------------------------------------------------------------

    async def _rest_get(self, path: str) -> dict:
        """GET a REST endpoint, re-authenticating once on session expiry (401)."""
        await self._ensure_authenticated()
        url = f"http://{self.host}{path}"
        async with self._auth_session.get(
            url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        ) as resp:
            if resp.status == 401:
                # Mark session expired; next poll will re-authenticate fresh
                self._authenticated = False
                _LOGGER.debug("Session expired on %s — will re-authenticate next poll", path)
                raise aiohttp.ClientResponseError(
                    resp.request_info, resp.history, status=401
                )
            resp.raise_for_status()
            return await resp.json(content_type=None)

    # -------------------------------------------------------------------------
    # GPS fetch (unauthenticated fallback chain)
    # -------------------------------------------------------------------------

    async def _fetch_gps_data(self) -> dict:
        """Fetch GPS data: /gps/status/ (auth) → /gps/ → /srv/gps."""
        if self._has_auth:
            try:
                data = await self._rest_get("/gps/status/")
                _LOGGER.debug("GPS data from /gps/status/")
                return data
            except Exception as err:
                _LOGGER.debug("GPS /gps/status/ failed: %s", err)

        for path in ("/gps/", "/srv/gps"):
            try:
                url = f"http://{self.host}{path}"
                async with self.session.get(
                    url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
                ) as resp:
                    if resp.status == 200 and "401lockedout" not in str(resp.url):
                        data = await resp.json(content_type=None)
                        _LOGGER.debug("GPS data from %s", path)
                        return data
            except Exception as err:
                _LOGGER.debug("GPS %s failed: %s", path, err)

        return {}

    # -------------------------------------------------------------------------
    # Data fetch
    # -------------------------------------------------------------------------

    async def _async_update_data(self) -> dict:
        """Fetch data from the Inseego M3000."""
        status_url = f"http://{self.host}/srv/status"
        usage_url = f"http://{self.host}/apps_home/usageinfo"

        try:
            # Fetch status data (unauthenticated)
            async with self.session.get(
                status_url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            ) as response:
                if "401lockedout" in str(response.url):
                    _LOGGER.warning(
                        "Device at %s is locked out — all requests redirected to lockout page. "
                        "Wait for lockout to expire or reboot the device.",
                        self.host,
                    )
                    raise UpdateFailed(
                        "Device is locked out — wait for lockout to expire or reboot the device"
                    )
                if response.status != 200:
                    raise UpdateFailed(f"HTTP {response.status}")
                try:
                    status_data = await response.json(content_type=None)
                except (ValueError, aiohttp.ContentTypeError) as err:
                    raw = await response.text() if not response.content.at_eof() else "(already read)"
                    _LOGGER.warning(
                        "Unexpected response from %s — %s. Body: %.200s",
                        status_url, err, raw,
                    )
                    raise UpdateFailed(f"Unexpected response format from device: {err}")
                if "statusData" not in status_data:
                    raise UpdateFailed("Invalid status response format")

            # Fetch usage data (unauthenticated)
            usage_data = {}
            try:
                async with self.session.get(
                    usage_url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
                ) as response:
                    if response.status == 200 and "401lockedout" not in str(response.url):
                        usage_data = await response.json(content_type=None)
            except Exception as err:
                _LOGGER.debug("Usage data not available: %s", err)

            # Fetch REST data (authenticated, skipped if no password configured)
            cellular_status_data = {}
            battery_status_data = {}
            device_info_data = {}
            account_info_data = {}
            if self._has_auth:
                for key, path, target in (
                    ("cellular", "/rest/1.0/CellularServiceStatus", None),
                    ("battery",  "/rest/1.0/BatteryStatus",         None),
                    ("device",   "/rest/1.0/DeviceInfo",            None),
                    ("account",  "/rest/1.0/AccountInfo",           None),
                ):
                    try:
                        result = await self._rest_get(path)
                        if key == "cellular":
                            cellular_status_data = result
                        elif key == "battery":
                            battery_status_data = result
                        elif key == "device":
                            device_info_data = result
                        elif key == "account":
                            account_info_data = result
                    except Exception as err:
                        _LOGGER.debug("%s REST fetch failed: %s", key, err)

            # Fetch GPS data with fallback chain
            gps_data = await self._fetch_gps_data()

            return {
                **status_data,
                "usageData": usage_data,
                "cellularStatusData": cellular_status_data,
                "batteryStatusData": battery_status_data,
                "deviceInfoData": device_info_data,
                "accountInfoData": account_info_data,
                "gpsData": gps_data,
            }

        except UpdateFailed:
            raise
        except TimeoutError:
            raise UpdateFailed(
                f"Timed out connecting to {self.host} — device may be offline or unreachable"
            )
        except aiohttp.ClientConnectorError:
            raise UpdateFailed(
                f"Cannot connect to {self.host} — check the IP address and network"
            )
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with device: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")
