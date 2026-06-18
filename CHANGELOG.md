# Changelog

All notable changes to this project will be documented in this file.
## [1.6.0] - 2026-06-18

### New switches (requires password)
- **WiFi** — enable/disable the hotspot's WiFi radio
- **Mobile Data** — enable/disable cellular data
- **GPS** — enable/disable the GPS receiver
- **Ethernet Port** — enable/disable the physical Ethernet port

All switches show as unavailable if no admin password is configured.

### New button (requires password)
- **Reboot** — restart the device

## [1.5.0] - 2026-06-18

### Authentication
Optional admin password in the setup flow unlocks the device REST API. Implements the M3000 bcrypt login flow in pure Python (no native library dependency). Without a password the integration works exactly as before.

### New sensors — authenticated (requires password)

**Cellular signal detail (from `/rest/1.0/CellularServiceStatus`):**
- Signal Strength RSRP (dBm)
- Signal Quality RSRQ (dB) — disabled by default
- Signal to Noise SINR (dB) — disabled by default
- Active Band (e.g. n25, n41)
- Roaming State
- 5G Bandwidth (MHz) — disabled by default
- Cell ID — disabled by default
- Physical Cell ID PCI — disabled by default

**Battery (from `/rest/1.0/BatteryStatus`):**
- Battery Charging Source (e.g. WallCharger)

**Device identity (from `/rest/1.0/DeviceInfo` and `/rest/1.0/AccountInfo`):**
- IMEI, MAC Address, ICCID, MDN — disabled by default
- Hardware Version, Modem Firmware, Web UI Version — disabled by default

### New sensors — GPS location

Sourced from `/gps/status/` (authenticated) with automatic fallback to `/gps/` then `/srv/gps` for older firmware. All disabled by default, diagnostic category, require a GPS fix:
- Latitude (°), Longitude (°)
- Altitude (ft), Heading (°)
- Accuracy (m), Satellites

### New binary sensor
- WAN Connected — true internet connectivity check: cellular connection state AND a WAN IP assigned; distinct from the existing Connection sensor

### Reliability improvements
- Device lockout detection: requests redirected to `401lockedout.html` now raise a clear error instead of silently failing
- Active Band, Technology, 5G Bandwidth, and PCI fall back to `/srv/status` values when the REST API is unavailable, instead of showing Unknown
- Timeout and connection-refused errors produce distinct log messages
- Raw response body logged on JSON parse failure to aid diagnosis
- Fixed blocking event loop warning on newer HA versions (Python 3.14)
- Session expiry handled gracefully — REST sensors miss one poll then recover automatically

## [1.0.5] - 2026-01-13
- Bug fix missing function import [#8](https://github.com/sjoerger/inseego_m3000/issues/8)

## [1.0.4] - 2026-01-13
- Added local icon.png file
- Fix unhandled exception not raising AbortFlow for duplicate devices. Fixes [#4](https://github.com/sjoerger/inseego_m3000/issues/4)
- Updated several sensors to be categorized as diagnostic entities. Resolves [#6](https://github.com/sjoerger/inseego_m3000/issues/6)
- Updated a few binary sensor names

## [1.0.3] - 2026-01-13
- Updated README with missing images
- Removed unneeded installation instructions
- Added one click install with HACS link
- Disable specific sensor entities by default. Fixes [#1](https://github.com/sjoerger/inseego_m3000/issues/1)

## [1.0.2] - 2026-01-10
- Fix URLs for hotspot status and info data. Should've double checked this to before starting
- Removed redundant files

## [1.0.1] - 2026-01-10
- Hopefully this fixes the HACS not showing any information about the integration
- Other repo organization to make HACS validation work
- No code changes

## [1.0.0] - 2026-01-09

### Added
- Initial release of Inseego M3000 Hotspot integration
- Support for 24 sensor entities:
  - Signal Strength (with network details)
  - Signal to Noise Ratio (SNR)
  - Battery percentage
  - Network provider
  - Network technology
  - Connection state
  - Data received (session)
  - Data transmitted (session)
  - Total data usage (session)
  - Connection duration
  - Connected clients count
  - WiFi clients count
  - Primary clients count
  - IP address (with gateway and subnet info)
  - SIM status
  - GPS status
  - Current billing cycle usage
  - Current cycle download
  - Current cycle upload
  - Data allowance
  - Data remaining
  - Data allowance remaining (percentage)
  - Days until cycle reset
  - Billing cycle end date
- Support for 8 binary sensor entities:
  - Connection status
  - WiFi enabled
  - Mobile data enabled
  - Battery charging status
  - Battery present
  - Ethernet connection
  - Airplane mode
  - Guest WiFi enabled
- UI-based configuration through Home Assistant's config flow
- Automatic device discovery and entity creation
- Configurable update interval (10-300 seconds)
- Proper device registry integration
- Support for Home Assistant statistics and long-term data
- Comprehensive error handling and logging

### Technical Details
- Uses Home Assistant's DataUpdateCoordinator for efficient polling
- Fetches data from two API endpoints (status and usage)
- Implements proper entity descriptions with device classes
- Supports state classes for statistics
- Includes proper unit of measurement for all sensors
- All entities are linked to a single device in the device registry
- Graceful handling of missing usage data (optional endpoint)

### Documentation
- Complete README with features and usage
- Installation guide with troubleshooting
- Example dashboard configurations
- Example automations for common use cases

## Future Enhancements (Planned)

### Version 1.1.0
- [ ] Add support for SMS message count sensor
- [ ] Add support for software update notification
- [ ] Include more detailed battery information (health mode, charging source)
- [ ] Add configurable data usage reset

### Version 1.2.0
- [ ] Support for device control (toggle WiFi, etc.) if API permits
- [ ] Add diagnostics support
- [ ] Implement options flow for changing settings after setup

### Version 2.0.0
- [ ] Support for multiple SIM cards (if API provides this data)
- [ ] Advanced network statistics and band aggregation details
- [ ] Support for connected device details (individual client info)
