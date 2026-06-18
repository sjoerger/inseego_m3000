"""Button platform for Inseego M3000 Hotspot."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity

_LOGGER = logging.getLogger(__name__)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InseegoM3000DataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Inseego M3000 buttons from a config entry."""
    coordinator: InseegoM3000DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([InseegoM3000RebootButton(coordinator)])


class InseegoM3000RebootButton(CoordinatorEntity, ButtonEntity):
    """Button to reboot the Inseego M3000."""

    _attr_has_entity_name = True
    _attr_name = "Reboot"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator: InseegoM3000DataUpdateCoordinator) -> None:
        """Initialize the reboot button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_reboot"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"Inseego M3000 ({coordinator.host})",
            "manufacturer": "Inseego",
            "model": "M3000",
        }

    @property
    def available(self) -> bool:
        """Reboot requires authentication."""
        return super().available and self.coordinator._has_auth

    async def async_press(self) -> None:
        """Reboot the device."""
        _LOGGER.info("%s: rebooting device", self.coordinator.host)
        result = await self.coordinator._rest_post("/restarting/reboot/")
        if result.get("success", result.get("status") == 200):
            _LOGGER.info("%s: reboot acknowledged", self.coordinator.host)
        else:
            _LOGGER.warning("%s: no success acknowledgement for reboot: %s",
                            self.coordinator.host, result)
