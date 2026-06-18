# Inseego M3000 Hotspot Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

A Home Assistant custom integration for monitoring Inseego M3000 portable hotspots.

## Features

### 📡 Connection & Signal
- Signal strength (bars and SNR)
- Network provider and technology (4G/5G/5G UWB)
- Connection state and duration
- WAN connectivity (true internet check — connected state + WAN IP)
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
- Battery percentage, charging status, and charging source
- WiFi, mobile data, and ethernet status
- Connected clients count
- SIM and GPS status

### 🔐 Authenticated sensors (optional admin password)
When an admin password is configured, the integration unlocks additional sensors via the device REST API:

**Cellular signal detail:**
- RSRP (dBm), RSRQ (dB), SINR (dB)
- Active band, roaming state, 5G bandwidth, Cell ID, PCI

**Device identity (diagnostic):**
- IMEI, MAC address, ICCID, MDN
- Hardware version, modem firmware, web UI version

## Installation

### HACS (Recommended)

One-click installation from HACS:

[![Open your Home Assistant instance and open the Inseego M3000 integration inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sjoerger&repository=inseego_m3000&category=integration)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/sjoerger/inseego_m3000`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Inseego M3000" in HACS
8. Click "Download"
9. Restart Home Assistant
10. Add the integration via UI: Settings → Devices & Services → Add Integration → "Inseego M3000"


## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Inseego M3000"
4. Enter your hotspot's IP address (usually `192.168.1.1`)
5. Optionally enter your admin password to enable REST API sensors
6. Optionally adjust the update interval (default: 30 seconds)
7. Click Submit

The admin password is the same password used to log in to the hotspot's web UI. It is stored securely in Home Assistant's config entry storage. Without a password the integration works normally with unauthenticated endpoints only.

## Documentation

- [Installation Guide](INSTALLATION.md)
- [Dashboard Examples](EXAMPLES.md)
- [Changelog](CHANGELOG.md)

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
![Device Page](https://github.com/user-attachments/assets/aa908577-f281-4e02-bdf2-d0b2d50ead27)

### Sensors Example
![Sensors](https://github.com/user-attachments/assets/1d51724d-0574-4b26-8e9a-e96822755e21)


## Device Lockout

The M3000 will lock out all HTTP access (redirecting to `401lockedout.html`) after too many failed password attempts. This integration only reads data from the device and does not send passwords, so it will not trigger a lockout. If a lockout does occur (e.g. from another tool or browser), the integration will surface a clear error message rather than failing silently. The lockout clears on its own after a timeout or on device reboot.

## Supported Devices

- Inseego M3000 (tested)
- Potentially other Inseego hotspots with similar API (untested)

## API Information

**Unauthenticated endpoints (always polled):**
- `http://{device_ip}/srv/status` — device and connection status
- `http://{device_ip}/apps_home/usageinfo` — billing cycle data

**Authenticated endpoints (polled when password is configured):**
- `http://{device_ip}/rest/1.0/CellularServiceStatus` — detailed signal metrics
- `http://{device_ip}/rest/1.0/BatteryStatus` — charging source and health
- `http://{device_ip}/rest/1.0/DeviceInfo` — hardware details and firmware versions
- `http://{device_ip}/rest/1.0/AccountInfo` — SIM identity (ICCID, MDN)

## Contributing

Contributions are welcome! Please feel free to submit a [Pull Request](https://github.com/sjoerger/inseego_m3000/pulls).

## Issues / Support

If you encounter any issues, please:

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
