"""Switch platform for Inseego M3000 Hotspot."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

_LOGGER = logging.getLogger(__name__)

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InseegoM3000DataUpdateCoordinator


@dataclass
class InseegoSwitchEntityDescription(SwitchEntityDescription):
    """Describes an Inseego switch entity."""

    turn_on_path: str = ""
    turn_off_path: str = ""
    is_on_fn: Callable[[dict], bool] = None


def _ack_ok(result: dict) -> bool:
    """Return True if the device acknowledged the command successfully.

    Different endpoints return different shapes:
    - {"success": true/1}
    - {"status": 200}
    - Full page-state blob with "errorCount": 0 (e.g. GPS endpoints)
    """
    if result.get("success"):
        return True
    if result.get("status") == 200:
        return True
    if "errorCount" in result and result["errorCount"] == 0:
        return True
    return False


SWITCH_TYPES: tuple[InseegoSwitchEntityDescription, ...] = (
    InseegoSwitchEntityDescription(
        key="wifi",
        name="WiFi",
        icon="mdi:wifi",
        turn_on_path="/wifigeneral/enablewifi/",
        turn_off_path="/wifigeneral/disablewifi/",
        is_on_fn=lambda data: bool(data.get("statusData", {}).get("statusBarWiFiEnabled", 0)),
    ),
    InseegoSwitchEntityDescription(
        key="mobile_data",
        name="Mobile Data",
        icon="mdi:signal",
        turn_on_path="/wwan/enablecellulardata/",
        turn_off_path="/wwan/disablecellulardata/",
        is_on_fn=lambda data: bool(data.get("statusData", {}).get("statusBarMobileDataEnabled", 0)),
    ),
    InseegoSwitchEntityDescription(
        key="gps_enabled",
        name="GPS",
        icon="mdi:crosshairs-gps",
        turn_on_path="/gps/enablegps/",
        turn_off_path="/gps/disablegps/",
        is_on_fn=lambda data: not data.get("gpsData", {}).get("gpsIsOff", True),
    ),
    InseegoSwitchEntityDescription(
        key="ethernet_port",
        name="Ethernet Port",
        icon="mdi:ethernet",
        turn_on_path="/preferences/displayethernetenable/",
        turn_off_path="/preferences/displayethernetdisable/",
        is_on_fn=lambda data: data.get("statusData", {}).get(
            "statusBarEthernetPortEnabled", ""
        ) not in ("", "disabled", "0", 0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Inseego M3000 switches from a config entry."""
    coordinator: InseegoM3000DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        InseegoM3000Switch(coordinator, description) for description in SWITCH_TYPES
    )


class InseegoM3000Switch(CoordinatorEntity, SwitchEntity):
    """Representation of an Inseego M3000 switch."""

    entity_description: InseegoSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InseegoM3000DataUpdateCoordinator,
        description: InseegoSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"Inseego M3000 ({coordinator.host})",
            "manufacturer": "Inseego",
            "model": "M3000",
        }

    @property
    def available(self) -> bool:
        """Switches require authentication."""
        return super().available and self.coordinator._has_auth

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        _LOGGER.info("%s: turning on %s", self.coordinator.host, self.entity_description.name)
        result = await self.coordinator._rest_post(self.entity_description.turn_on_path)
        if _ack_ok(result):
            _LOGGER.info("%s: %s on acknowledged", self.coordinator.host, self.entity_description.name)
        else:
            _LOGGER.warning("%s: no success acknowledgement turning on %s: %s",
                            self.coordinator.host, self.entity_description.name, result)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        _LOGGER.info("%s: turning off %s", self.coordinator.host, self.entity_description.name)
        result = await self.coordinator._rest_post(self.entity_description.turn_off_path)
        if _ack_ok(result):
            _LOGGER.info("%s: %s off acknowledged", self.coordinator.host, self.entity_description.name)
        else:
            _LOGGER.warning("%s: no success acknowledgement turning off %s: %s",
                            self.coordinator.host, self.entity_description.name, result)
        await self.coordinator.async_request_refresh()
