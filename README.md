# Inseego M3000 Hotspot Integration for Home Assistant

This custom integration allows you to monitor your Inseego M3000 portable hotspot in Home Assistant.

## Features

This integration provides comprehensive monitoring of your Inseego M3000 hotspot including:

### Sensors
- **Signal Strength** - Signal bars (0-5) with network details
- **Signal to Noise Ratio (SNR)** - SNR in dB
- **Battery** - Battery percentage
- **Network** - Current network provider
- **Technology** - Current network technology (4G, 5G, 5G UWB, etc.)
- **Connection State** - Connection status
- **Data Received** - Total bytes received (session)
- **Data Transmitted** - Total bytes transmitted (session)
- **Total Data Usage** - Combined data usage (session)
- **Connection Duration** - How long the current connection has been active
- **Connected Clients** - Total number of connected devices
- **WiFi Clients** - Number of WiFi clients
- **Primary Clients** - Number of primary network clients
- **IP Address** - Current public IP with gateway and subnet info
- **SIM Status** - SIM card status
- **GPS Status** - GPS fix status
- **Current Billing Cycle Usage** - Total data used this billing period
- **Current Cycle Download** - Download data this billing period
- **Current Cycle Upload** - Upload data this billing period
- **Data Allowance** - Monthly data allowance
- **Data Remaining** - Remaining data allowance
- **Data Allowance Remaining** - Percentage of allowance remaining
- **Days Until Cycle Reset** - Days left in current billing cycle
- **Billing Cycle End Date** - When the current billing cycle ends

### Binary Sensors
- **Connection** - Whether device is connected to network
- **WiFi** - WiFi enabled status
- **Mobile Data** - Mobile data enabled status
- **Battery Charging** - Whether battery is charging
- **Battery Present** - Battery detection status
- **Ethernet** - Ethernet connection status
- **Airplane Mode** - Airplane mode status
- **Guest WiFi** - Guest WiFi enabled status

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `inseego_m3000` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Inseego M3000"
4. Enter your device's IP address (typically 192.168.1.1 or similar)
5. Optionally adjust the update interval (default: 30 seconds)
6. Click Submit

## Finding Your Device IP

The default IP address for Inseego M3000 hotspots is usually:
- **192.168.1.1** (when connected via WiFi)
- Check your hotspot's display screen for the exact IP
- Check your router/network settings for the device IP

## Usage

After configuration, all sensors and binary sensors will be automatically created under a single device. You can:

- View all entities in the device page
- Create automations based on signal strength, battery level, data usage, etc.
- Add entities to your dashboard
- Monitor network technology changes (4G → 5G transitions)
- Track data usage over time with the statistics feature

### Example Automations

**Low Battery Alert:**
```yaml
automation:
  - alias: "Hotspot Low Battery"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Hotspot battery is low ({{ states('sensor.inseego_m3000_battery') }}%)"
```

**Poor Signal Warning:**
```yaml
automation:
  - alias: "Hotspot Poor Signal"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_signal_strength
        below: 2
    action:
      - service: notify.mobile_app
        data:
          message: "Hotspot has poor signal ({{ states('sensor.inseego_m3000_signal_strength') }} bars)"
```

**High Data Usage Alert:**
```yaml
automation:
  - alias: "Hotspot High Data Usage"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_total_data_usage
        above: 50000000000  # 50 GB in bytes
    action:
      - service: notify.mobile_app
        data:
          message: "Hotspot has used over 50GB of data"
```

**Billing Cycle Data Alert:**
```yaml
automation:
  - alias: "Hotspot 80% Data Used"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_data_allowance_remaining
        below: 20  # 20% remaining
    action:
      - service: notify.mobile_app
        data:
          message: "Only {{ states('sensor.inseego_m3000_data_allowance_remaining') }}% of data allowance remaining!"
```

**Billing Cycle Reset Reminder:**
```yaml
automation:
  - alias: "Billing Cycle Ending Soon"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_days_until_cycle_reset
        below: 3
    action:
      - service: notify.mobile_app
        data:
          message: "Billing cycle ends in {{ states('sensor.inseego_m3000_days_until_cycle_reset') }} days"
```

## Troubleshooting

### Connection Issues
- Ensure your Home Assistant instance can reach the hotspot's IP address
- Check that the hotspot is powered on and functioning
- Try pinging the IP address from your Home Assistant host
- Verify you're using the correct IP address

### Entities Not Updating
- Check the update interval in the integration configuration
- Review Home Assistant logs for errors
- Ensure the hotspot firmware is up to date

### Missing Entities
- Some entities may not appear if the hotspot doesn't provide that data
- Different firmware versions may have slightly different API responses

## API Information

This integration uses the Inseego M3000's REST API endpoints:
- **Status Endpoint:** `http://{device_ip}/status_data.json`
- **Usage Endpoint:** `http://{device_ip}/getUsageInfo.json`
- **Method:** GET
- **Authentication:** None required (local network access)
- **Update Method:** Polling (both endpoints)

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Provide Home Assistant logs when reporting problems

## Credits

Developed for the Home Assistant community.

## License

MIT License - See LICENSE file for details
