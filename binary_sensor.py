"""Binary sensor platform for Inseego M3000 Hotspot."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InseegoM3000DataUpdateCoordinator


@dataclass
class InseegoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Inseego binary sensor entity."""

    value_fn: Callable[[dict], bool] = None


def is_connected(data: dict) -> bool:
    """Check if device is connected."""
    status_data = data.get("statusData", {})
    state = status_data.get("statusBarConnectionState", "")
    return state == "Connected"


def is_wifi_enabled(data: dict) -> bool:
    """Check if WiFi is enabled."""
    status_data = data.get("statusData", {})
    enabled = status_data.get("statusBarWiFiEnabled", 0)
    return bool(enabled)


def is_mobile_data_enabled(data: dict) -> bool:
    """Check if mobile data is enabled."""
    status_data = data.get("statusData", {})
    enabled = status_data.get("statusBarMobileDataEnabled", 0)
    return bool(enabled)


def is_charging(data: dict) -> bool:
    """Check if battery is charging."""
    status_data = data.get("statusData", {})
    charging = status_data.get("statusBarBatteryChargingState", "false")
    return charging.lower() == "true"


def is_battery_present(data: dict) -> bool:
    """Check if battery is present."""
    status_data = data.get("statusData", {})
    detection = status_data.get("statusBarBatteryDetection", "")
    return detection == "Present"


def is_ethernet_connected(data: dict) -> bool:
    """Check if ethernet is connected."""
    status_data = data.get("statusData", {})
    port_enabled = status_data.get("statusBarEthernetPortEnabled", "")
    return port_enabled == "connected"


def is_airplane_mode(data: dict) -> bool:
    """Check if airplane mode is on."""
    status_data = data.get("statusData", {})
    mode = status_data.get("statusBarAirplaneMode", "")
    return mode != "AirplaneModeOff"


def is_guest_wifi_enabled(data: dict) -> bool:
    """Check if guest WiFi is enabled."""
    status_data = data.get("statusData", {})
    enabled = status_data.get("statusBarGuestWifiEnabled", 0)
    return bool(enabled)


BINARY_SENSOR_TYPES: tuple[InseegoBinarySensorEntityDescription, ...] = (
    InseegoBinarySensorEntityDescription(
        key="connection",
        name="Connection",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=is_connected,
    ),
    InseegoBinarySensorEntityDescription(
        key="wifi",
        name="WiFi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:wifi",
        value_fn=is_wifi_enabled,
    ),
    InseegoBinarySensorEntityDescription(
        key="mobile_data",
        name="Mobile Data",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:signal",
        value_fn=is_mobile_data_enabled,
    ),
    InseegoBinarySensorEntityDescription(
        key="battery_charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=is_charging,
    ),
    InseegoBinarySensorEntityDescription(
        key="battery_present",
        name="Battery Present",
        device_class=BinarySensorDeviceClass.PLUG,
        icon="mdi:battery",
        value_fn=is_battery_present,
    ),
    InseegoBinarySensorEntityDescription(
        key="ethernet",
        name="Ethernet",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:ethernet",
        value_fn=is_ethernet_connected,
    ),
    InseegoBinarySensorEntityDescription(
        key="airplane_mode",
        name="Airplane Mode",
        icon="mdi:airplane",
        value_fn=is_airplane_mode,
    ),
    InseegoBinarySensorEntityDescription(
        key="guest_wifi",
        name="Guest WiFi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:wifi-star",
        value_fn=is_guest_wifi_enabled,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Inseego M3000 binary sensor based on a config entry."""
    coordinator: InseegoM3000DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        InseegoM3000BinarySensor(coordinator, description)
        for description in BINARY_SENSOR_TYPES
    ]

    async_add_entities(entities)


class InseegoM3000BinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Inseego M3000 binary sensor."""

    entity_description: InseegoBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InseegoM3000DataUpdateCoordinator,
        description: InseegoBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.host}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"Inseego M3000 ({coordinator.host})",
            "manufacturer": "Inseego",
            "model": "M3000",
            "sw_version": coordinator.data.get("statusData", {}).get(
                "StatusBarSoftwareUpdateSourceVersion", "Unknown"
            ),
        }

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return False
