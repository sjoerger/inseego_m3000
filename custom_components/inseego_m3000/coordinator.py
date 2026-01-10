"""DataUpdateCoordinator for Inseego M3000."""
from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class InseegoM3000DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Inseego M3000 data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.host = entry.data[CONF_HOST]
        self.session = async_get_clientsession(hass)
        
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the Inseego M3000."""
        status_url = f"http://{self.host}/srv/status"
        usage_url = f"http://{self.host}/apps_home/usageinfo"
        
        try:
            # Fetch status data
            async with self.session.get(
                status_url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"HTTP {response.status}")
                
                status_data = await response.json()
                
                if "statusData" not in status_data:
                    raise UpdateFailed("Invalid status response format")
            
            # Fetch usage data
            usage_data = {}
            try:
                async with self.session.get(
                    usage_url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        usage_data = await response.json()
            except Exception as err:
                _LOGGER.debug("Usage data not available: %s", err)
            
            # Combine both datasets
            return {
                **status_data,
                "usageData": usage_data
            }
                
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with device: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")
