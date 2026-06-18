# Inseego M3000 Integration - AI Coding Instructions

## Project Overview

This is a **Home Assistant custom integration** for monitoring Inseego M3000 portable hotspots. It follows Home Assistant's async/await architecture with a coordinator pattern for data fetching and exposes 24 sensors and 8 binary sensors for monitoring connectivity, data usage, battery, and device status.

## Architecture Overview

### Component Structure
- **Domain**: `inseego_m3000` (defined in `const.py`)
- **Coordinator**: `InseegoM3000DataUpdateCoordinator` - centralized async data fetching
- **Platforms**: Sensor and binary sensor entities expose device metrics
- **Device Type**: Local polling integration (`iot_class: local_polling`)

### Data Flow
```
Inseego M3000 (HTTP Endpoints)
    ↓
Coordinator (async_update_data)
    ├── GET /srv/status → statusData
    └── GET /apps_home/usageinfo → usageData
    ↓
Sensor/Binary Sensor Entities (value_fn extracts values)
    ↓
Home Assistant State Machine
```

### Coordinator Pattern (`coordinator.py`)
- Inherits from `DataUpdateCoordinator` - handles scheduling and error propagation
- `_async_update_data()` fetches from two HTTP endpoints and merges results
- Respects `CONF_SCAN_INTERVAL` (default 30s, range 10-300s) from config
- Raises `UpdateFailed` on connection errors - coordinator retries automatically
- Combines status and usage data into single dict for entity consumption

## Code Patterns & Conventions

### Entity Value Extraction
Use **value functions** in entity descriptions to extract data from coordinator output:
```python
# Pattern: extract from nested dict with fallback/type conversion
def get_signal_bars(data: dict) -> int:
    status_data = data.get("statusData", {})
    bars = status_data.get("statusBarSignalBars", "0")
    try:
        return int(bars)  # API returns strings, convert to appropriate type
    except (ValueError, TypeError):
        return 0  # Graceful fallback for missing/invalid data
```

**Key details:**
- All API responses are dictionaries with string values
- Always wrap type conversions in try/except
- Return sensible defaults (0, False, empty string)
- Functions named with entity type prefix: `get_*` for sensors, `is_*` for binary sensors

### Entity Descriptions
Define reusable entity metadata using dataclasses:
```python
@dataclass
class InseegoSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict], StateType] = None
    attributes_fn: Callable[[dict], dict] = None
```

Both `sensor.py` and `binary_sensor.py` use this pattern.

### Entity Platform Setup
Standard Home Assistant platform pattern:
```python
async def async_setup_entry(hass, entry, async_add_entities, discovery_info=None):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        InseegoSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)
```

## Configuration & Setup Flow

### Config Flow (`config_flow.py`)
1. User inputs host IP (required) and optional scan interval (10-300s)
2. `validate_connection()` tests connectivity and validates API response
3. Checks for duplicate configuration using `async_set_unique_id()`
4. Creates config entry with input data
5. **Validation errors**: `cannot_connect` (HTTP/network), `invalid_device` (bad response), `unknown` (other)

### Integration Setup (`__init__.py`)
1. Instantiates `InseegoM3000DataUpdateCoordinator`
2. Calls `async_config_entry_first_refresh()` - must succeed or raise `ConfigEntryNotReady`
3. Stores coordinator in `hass.data[DOMAIN][entry.entry_id]`
4. Forwards setup to SENSOR and BINARY_SENSOR platforms

## API/Data Contract

### Status Endpoint: `GET http://{host}/srv/status`
Returns JSON with `statusData` object containing keys like:
- `statusBarSignalBars`, `statusBarSNR` - signal metrics
- `statusBarConnectionState`, `statusBarNetwork`, `statusBarTechnology` - connection info
- `statusBarBatteryPercent`, `statusBarBatteryChargingState`, `statusBarBatteryDetection` - battery
- `statusBarWiFiEnabled`, `statusBarMobileDataEnabled`, `statusBarEthernetPortEnabled` - interfaces
- `statusBarBytesReceived`, `statusBarBytesSent`, `statusBarTotalBytes` - data usage
- All values are **strings** or booleans - coordinate expects this

### Usage Endpoint: `GET http://{host}/apps_home/usageinfo` (optional)
Returns billing cycle and session data. If unavailable, logged as debug, doesn't fail integration.

## Adding New Sensors/Binary Sensors

### For Sensors:
1. Create value function in `sensor.py` following `get_*` naming
2. Add `SensorEntityDescription` to `SENSOR_DESCRIPTIONS` list
3. Set appropriate `native_unit_of_measurement` and `device_class`
4. Optional: add `attributes_fn` for additional attributes

### For Binary Sensors:
1. Create value function in `binary_sensor.py` following `is_*` naming
2. Add `BinarySensorEntityDescription` to `BINARY_SENSOR_DESCRIPTIONS` list
3. Set `device_class` (e.g., `BinarySensorDeviceClass.CONNECTIVITY`)

### Example Addition:
```python
def get_new_metric(data: dict) -> int:
    status_data = data.get("statusData", {})
    value = status_data.get("newMetricKey", "0")
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
```

## Dependencies & Environment

- **aiohttp>=3.8.0**: Async HTTP client for device communication
- **Home Assistant Core**: async/await patterns, config entries, entity platform
- No external device libraries - directly queries HTTP API

## Testing Patterns

- Integration uses Home Assistant test utilities
- Config flow validation tested via `validate_connection()` mock
- Entity value extraction tested with sample `statusData` dicts
- Coordinator tested with mock HTTP responses and timeout scenarios

## Key File References

- [coordinator.py](../custom_components/inseego_m3000/coordinator.py) - Data fetching & refresh logic
- [sensor.py](../custom_components/inseego_m3000/sensor.py) - Sensor entity definitions (440 lines)
- [binary_sensor.py](../custom_components/inseego_m3000/binary_sensor.py) - Binary sensor entities (188 lines)
- [config_flow.py](../custom_components/inseego_m3000/config_flow.py) - User configuration
- [const.py](../custom_components/inseego_m3000/const.py) - Constants & defaults
- [__init__.py](../custom_components/inseego_m3000/__init__.py) - Integration setup/teardown

## Common Tasks

**Add a new sensor**: Add value function → Create description object → Add to SENSOR_DESCRIPTIONS  
**Fix data parsing**: Check value_fn in sensor.py/binary_sensor.py → handle string/type conversions  
**Change update interval**: Modify DEFAULT_SCAN_INTERVAL in const.py (affects all instances)  
**Test API connectivity**: Call `validate_connection()` with test host  
**Debug coordinator issues**: Check `_LOGGER.debug()` calls in coordinator.py for HTTP/parsing errors

