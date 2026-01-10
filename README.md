# Inseego M3000 Hotspot Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

A Home Assistant custom integration for monitoring Inseego M3000 portable hotspots.

## Features

Monitor your Inseego M3000 hotspot with 24 sensors and 8 binary sensors including:

### 📡 Connection & Signal
- Signal strength (bars and SNR)
- Network provider and technology (4G/5G/5G UWB)
- Connection state and duration
- IP address information

### 📊 Data Usage
**Session Data:**
- Real-time data received/transmitted/total

**Billing Cycle Data:**
- Monthly usage tracking
- Data allowance and remaining
- Download/Upload breakdown
- Days until cycle reset
- Cycle end date

### 🔋 Device Status
- Battery percentage and charging status
- WiFi, mobile data, and ethernet status
- Connected clients count
- SIM and GPS status

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/sjoerger/inseego_m3000`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "Inseego M3000" in HACS
9. Click "Download"
10. Restart Home Assistant
11. Add the integration via UI: Settings → Devices & Services → Add Integration → "Inseego M3000"

### Manual Installation

1. Download the `inseego_m3000` folder from this repository
2. Copy it to your `<config>/custom_components/` directory
3. Restart Home Assistant
4. Add the integration via UI: Settings → Devices & Services → Add Integration → "Inseego M3000"

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Inseego M3000"
4. Enter your hotspot's IP address (usually `192.168.1.1`)
5. Optionally adjust the update interval (default: 30 seconds)
6. Click Submit

## Documentation

- [Installation Guide](custom_components/inseego_m3000/INSTALLATION.md)
- [Dashboard Examples](custom_components/inseego_m3000/EXAMPLES.md)
- [Changelog](custom_components/inseego_m3000/CHANGELOG.md)

## Example Automations

### Low Battery Alert
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
          message: "Hotspot battery is at {{ states('sensor.inseego_m3000_battery') }}%"
```

### Data Usage Warning
```yaml
automation:
  - alias: "Data Usage Warning - 80%"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_data_allowance_remaining
        below: 20  # 20% remaining
    action:
      - service: notify.mobile_app
        data:
          message: "Only {{ states('sensor.inseego_m3000_data_remaining') }} GB remaining!"
```

## Screenshots

### Device Page
![Device Page](images/device_page.png)

### Dashboard Example
![Dashboard](images/dashboard.png)

## Supported Devices

- Inseego M3000 (tested)
- Potentially other Inseego hotspots with similar API (untested)

## API Information

This integration uses the following REST API endpoints:
- `http://{device_ip}/status_data.json` - Device and connection status
- `http://{device_ip}/getUsageInfo.json` - Billing cycle data

No authentication is required for local network access.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any issues, please [open an issue](https://github.com/sjoerger/inseego_m3000/issues) with:
- Home Assistant version
- Integration version
- Relevant logs
- Steps to reproduce

## Support

- [Report a Bug](https://github.com/sjoerger/inseego_m3000/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/sjoerger/inseego_m3000/issues/new?template=feature_request.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Home Assistant community
- Inspired by the need for better hotspot monitoring

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/sjoerger/inseego_m3000.svg
[commits]: https://github.com/sjoerger/inseego_m3000/commits/main
[license-shield]: https://img.shields.io/github/license/sjoerger/inseego_m3000.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-sjoerger-blue.svg
[releases-shield]: https://img.shields.io/github/release/sjoerger/inseego_m3000.svg
[releases]: https://github.com/sjoerger/inseego_m3000/releases
