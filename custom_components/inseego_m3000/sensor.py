"""Sensor platform for Inseego M3000 Hotspot."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InseegoM3000DataUpdateCoordinator


@dataclass
class InseegoSensorEntityDescription(SensorEntityDescription):
    """Describes Inseego sensor entity."""

    value_fn: Callable[[dict], StateType] = None
    attributes_fn: Callable[[dict], dict] = None


def get_signal_bars(data: dict) -> int:
    """Extract signal bars."""
    status_data = data.get("statusData", {})
    bars = status_data.get("statusBarSignalBars", "0")
    try:
        return int(bars)
    except (ValueError, TypeError):
        return 0


def get_battery_percent(data: dict) -> int:
    """Extract battery percentage."""
    status_data = data.get("statusData", {})
    percent = status_data.get("statusBarBatteryPercent", "0")
    try:
        return int(percent)
    except (ValueError, TypeError):
        return 0


def get_snr(data: dict) -> int:
    """Extract SNR."""
    status_data = data.get("statusData", {})
    snr = status_data.get("statusBarSNR", "0")
    try:
        return int(snr)
    except (ValueError, TypeError):
        return 0


def get_bytes_received(data: dict) -> int:
    """Extract bytes received."""
    status_data = data.get("statusData", {})
    bytes_rx = status_data.get("statusBarBytesReceived", "0")
    try:
        return int(bytes_rx)
    except (ValueError, TypeError):
        return 0


def get_bytes_transmitted(data: dict) -> int:
    """Extract bytes transmitted."""
    status_data = data.get("statusData", {})
    bytes_tx = status_data.get("statusBarBytesTransmitted", "0")
    try:
        return int(bytes_tx)
    except (ValueError, TypeError):
        return 0


def get_bytes_total(data: dict) -> int:
    """Extract total bytes."""
    status_data = data.get("statusData", {})
    bytes_total = status_data.get("statusBarBytesTotal", "0")
    try:
        return int(bytes_total)
    except (ValueError, TypeError):
        return 0


def get_connection_duration(data: dict) -> int:
    """Extract connection duration in seconds."""
    status_data = data.get("statusData", {})
    duration = status_data.get("statusBarConnectionDuration", "0")
    try:
        return int(duration)
    except (ValueError, TypeError):
        return 0


def get_connected_clients(data: dict) -> int:
    """Extract connected clients count."""
    status_data = data.get("statusData", {})
    count = status_data.get("statusBarClientListSize", "0")
    try:
        return int(count)
    except (ValueError, TypeError):
        return 0


def get_wifi_clients(data: dict) -> int:
    """Extract WiFi clients count."""
    status_data = data.get("statusData", {})
    count = status_data.get("statusBarWiFiClientListSize", "0")
    try:
        return int(count)
    except (ValueError, TypeError):
        return 0


def get_primary_clients(data: dict) -> int:
    """Extract primary clients count."""
    status_data = data.get("statusData", {})
    count = status_data.get("statusBarPrimaryClientListSize", "0")
    try:
        return int(count)
    except (ValueError, TypeError):
        return 0


def get_network_attributes(data: dict) -> dict:
    """Get network-related attributes."""
    status_data = data.get("statusData", {})
    return {
        "network": status_data.get("statusBarNetwork", "Unknown"),
        "network_id": status_data.get("statusBarNetworkID", "Unknown"),
        "carrier": status_data.get("statusBarCarrier", "Unknown"),
        "technology": status_data.get("statusBarTechnology", "Unknown"),
        "band": status_data.get("statusBarBand", "Unknown").strip(),
        "bandwidth": status_data.get("statusBarBandwidth", "Unknown").strip(),
        "pci": status_data.get("statusBarPCI", "Unknown"),
    }


def get_ip_attributes(data: dict) -> dict:
    """Get IP-related attributes."""
    status_data = data.get("statusData", {})
    return {
        "ip_address": status_data.get("internetStatusIPAddress", "Unknown"),
        "ipv6_address": status_data.get("internetStatusIPv6Address", "Unknown"),
        "gateway": status_data.get("internetStatusGateway", "Unknown"),
        "subnet_mask": status_data.get("internetStatusSubnetMask", "Unknown"),
    }


SENSOR_TYPES: tuple[InseegoSensorEntityDescription, ...] = (
    InseegoSensorEntityDescription(
        key="signal_strength",
        name="Signal Strength",
        icon="mdi:signal",
        native_unit_of_measurement="bars",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_signal_bars,
        attributes_fn=get_network_attributes,
    ),
    InseegoSensorEntityDescription(
        key="snr",
        name="Signal to Noise Ratio",
        icon="mdi:signal-variant",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_snr,
    ),
    InseegoSensorEntityDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_battery_percent,
    ),
    InseegoSensorEntityDescription(
        key="network",
        name="Network",
        icon="mdi:network",
        value_fn=lambda data: data.get("statusData", {}).get("statusBarNetwork", "Unknown"),
        attributes_fn=get_network_attributes,
    ),
    InseegoSensorEntityDescription(
        key="technology",
        name="Technology",
        icon="mdi:radio-tower",
        value_fn=lambda data: data.get("statusData", {}).get("statusBarTechnology", "Unknown"),
    ),
    InseegoSensorEntityDescription(
        key="connection_state",
        name="Connection State",
        icon="mdi:connection",
        value_fn=lambda data: data.get("statusData", {}).get("statusBarConnectionState", "Unknown"),
    ),
    InseegoSensorEntityDescription(
        key="bytes_received",
        name="Data Received",
        icon="mdi:download",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_bytes_received,
    ),
    InseegoSensorEntityDescription(
        key="bytes_transmitted",
        name="Data Transmitted",
        icon="mdi:upload",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_bytes_transmitted,
    ),
    InseegoSensorEntityDescription(
        key="bytes_total",
        name="Total Data Usage",
        icon="mdi:chart-line",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_bytes_total,
    ),
    InseegoSensorEntityDescription(
        key="connection_duration",
        name="Connection Duration",
        icon="mdi:timer",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_connection_duration,
    ),
    InseegoSensorEntityDescription(
        key="connected_clients",
        name="Connected Clients",
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_connected_clients,
    ),
    InseegoSensorEntityDescription(
        key="wifi_clients",
        name="WiFi Clients",
        icon="mdi:wifi",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_wifi_clients,
    ),
    InseegoSensorEntityDescription(
        key="primary_clients",
        name="Primary Clients",
        icon="mdi:account-network",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_primary_clients,
    ),
    InseegoSensorEntityDescription(
        key="ip_address",
        name="IP Address",
        icon="mdi:ip-network",
        value_fn=lambda data: data.get("statusData", {}).get("internetStatusIPAddress", "Unknown"),
        attributes_fn=get_ip_attributes,
    ),
    InseegoSensorEntityDescription(
        key="sim_status",
        name="SIM Status",
        icon="mdi:sim",
        value_fn=lambda data: data.get("statusData", {}).get("statusBarSimStatus", "Unknown"),
    ),
    InseegoSensorEntityDescription(
        key="gps_status",
        name="GPS Status",
        icon="mdi:crosshairs-gps",
        value_fn=lambda data: data.get("statusData", {}).get("statusBarGpsStatus", "Unknown"),
    ),
    # Usage data sensors
    InseegoSensorEntityDescription(
        key="billing_cycle_usage",
        name="Current Billing Cycle Usage",
        icon="mdi:chart-timeline-variant",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: float(data.get("usageData", {}).get("lineUsage", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_rx_usage",
        name="Current Cycle Download",
        icon="mdi:download",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: float(data.get("usageData", {}).get("rxUsage", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_tx_usage",
        name="Current Cycle Upload",
        icon="mdi:upload",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: float(data.get("usageData", {}).get("txUsage", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_allowance",
        name="Data Allowance",
        icon="mdi:database",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_display_precision=2,
        value_fn=lambda data: float(data.get("usageData", {}).get("allowance", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_remaining",
        name="Data Remaining",
        icon="mdi:database-arrow-down",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: float(data.get("usageData", {}).get("remainingUsage", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_percentage_remaining",
        name="Data Allowance Remaining",
        icon="mdi:percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("usageData", {}).get("barPercentageRemaining", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_days_left",
        name="Days Until Cycle Reset",
        icon="mdi:calendar-clock",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("usageData", {}).get("daysLeft", "0")),
    ),
    InseegoSensorEntityDescription(
        key="billing_cycle_end",
        name="Billing Cycle End Date",
        icon="mdi:calendar-end",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: data.get("usageData", {}).get("cycleEndDt", "Unknown").replace("&#x2F;", "/"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Inseego M3000 sensor based on a config entry."""
    coordinator: InseegoM3000DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        InseegoM3000Sensor(coordinator, description)
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class InseegoM3000Sensor(CoordinatorEntity, SensorEntity):
    """Representation of an Inseego M3000 sensor."""

    entity_description: InseegoSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InseegoM3000DataUpdateCoordinator,
        description: InseegoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
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
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if self.entity_description.attributes_fn:
            return self.entity_description.attributes_fn(self.coordinator.data)
        return {}
