# Integration Update - Billing Cycle Data Added

## What's New

The integration has been updated to include **billing cycle data** from the `/getUsageInfo.json` API endpoint.

## New Sensors (8 additional)

1. **Current Billing Cycle Usage** - Total data used this billing period (GB)
2. **Current Cycle Download** - Download data this billing period (GB)
3. **Current Cycle Upload** - Upload data this billing period (GB)
4. **Data Allowance** - Monthly data allowance (GB)
5. **Data Remaining** - Remaining data allowance (GB)
6. **Data Allowance Remaining** - Percentage of allowance remaining (%)
7. **Days Until Cycle Reset** - Days left in current billing cycle
8. **Billing Cycle End Date** - When the current billing cycle ends

## Total Sensors: 24 + 8 Binary Sensors = 32 Entities

### Previous: 16 sensors
### Now: 24 sensors

## Technical Changes

### coordinator.py
- Now fetches from TWO API endpoints:
  - `http://{device_ip}/status_data.json` - Connection and device status
  - `http://{device_ip}/getUsageInfo.json` - Billing cycle data
- Gracefully handles if usage endpoint is unavailable
- Combines both datasets into a single data structure

### sensor.py
- Added 8 new sensor entity descriptions
- All billing sensors use proper units (GB, %, days, date)
- Proper state classes for statistics tracking
- Display precision set to 2 decimal places for GB values

### Documentation Updates
- README.md - Updated feature list and examples
- EXAMPLES.md - Added billing cycle dashboard cards
- CHANGELOG.md - Updated with new sensors
- QUICK_START.md - Updated sensor counts and categories

## Use Cases for New Sensors

### 1. Data Overage Prevention
Monitor your data usage throughout the billing cycle and get alerts before hitting your limit.

```yaml
automation:
  - alias: "Data Usage Warning - 80%"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_data_allowance_remaining
        below: 20  # 20% remaining = 80% used
    action:
      - service: notify.mobile_app
        data:
          message: "Warning: {{ states('sensor.inseego_m3000_current_billing_cycle_usage') }} GB of {{ states('sensor.inseego_m3000_data_allowance') }} GB used!"
```

### 2. Billing Cycle Tracking
See exactly how much data you have left and when your cycle resets.

Dashboard card:
```yaml
type: gauge
entity: sensor.inseego_m3000_data_allowance_remaining
name: Data Remaining
min: 0
max: 100
severity:
  green: 50
  yellow: 25
  red: 0
```

### 3. Usage Pattern Analysis
Track download vs upload patterns to understand your usage.

```yaml
type: entities
title: This Month's Usage
entities:
  - sensor.inseego_m3000_current_billing_cycle_usage
  - sensor.inseego_m3000_current_cycle_download
  - sensor.inseego_m3000_current_cycle_upload
```

### 4. Cycle End Reminders
Get notified when your billing cycle is about to reset.

```yaml
automation:
  - alias: "Billing Cycle Ending"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_days_until_cycle_reset
        below: 3
    action:
      - service: notify.mobile_app
        data:
          message: "Billing cycle ends in {{ states('sensor.inseego_m3000_days_until_cycle_reset') }} days on {{ states('sensor.inseego_m3000_billing_cycle_end_date') }}"
```

## Differences Between Session and Billing Data

The integration now provides TWO types of data usage:

### Session Data (from status_data.json)
- `sensor.inseego_m3000_bytes_received` - Bytes since last connection
- `sensor.inseego_m3000_bytes_transmitted` - Bytes since last connection
- `sensor.inseego_m3000_total_data_usage` - Combined session data
- Resets when device disconnects/reconnects

### Billing Cycle Data (from getUsageInfo.json)
- `sensor.inseego_m3000_current_billing_cycle_usage` - Total for the month
- `sensor.inseego_m3000_current_cycle_download` - Monthly download
- `sensor.inseego_m3000_current_cycle_upload` - Monthly upload
- Resets on billing cycle date

**Use session data for:** Real-time monitoring of current connection
**Use billing data for:** Monthly allowance tracking and overage prevention

## Backward Compatibility

✅ **Fully backward compatible** - All existing sensors remain unchanged
✅ **Graceful degradation** - If usage endpoint fails, device still works with status sensors
✅ **No configuration changes needed** - Existing installations will automatically get new sensors

## Installation

No changes needed if you already have the integration installed. Simply:
1. Replace the files in `custom_components/inseego_m3000/`
2. Restart Home Assistant
3. The new sensors will appear automatically

## Example Dashboard

Here's a complete card showing all billing information:

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.inseego_m3000_data_allowance_remaining
    name: Data Remaining
    min: 0
    max: 100
    needle: true
    
  - type: entities
    title: Billing Cycle Details
    entities:
      - entity: sensor.inseego_m3000_current_billing_cycle_usage
        name: Used This Month
      - entity: sensor.inseego_m3000_data_allowance
        name: Monthly Allowance
      - entity: sensor.inseego_m3000_data_remaining
        name: Remaining
      - type: divider
      - entity: sensor.inseego_m3000_current_cycle_download
        name: Downloaded
      - entity: sensor.inseego_m3000_current_cycle_upload
        name: Uploaded
      - type: divider
      - entity: sensor.inseego_m3000_billing_cycle_end_date
        name: Cycle Ends
      - entity: sensor.inseego_m3000_days_until_cycle_reset
        name: Days Left
```

## Questions?

See the updated documentation:
- **README.md** - Full feature list
- **EXAMPLES.md** - More dashboard examples
- **INSTALLATION.md** - Troubleshooting guide
