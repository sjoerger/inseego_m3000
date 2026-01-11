# Changelog

All notable changes to this project will be documented in this file.

## [1.0.3] - 2025-01-XX - UNRELEASED
- Updated README with missing images
- Removed unneeded installation instructions
- Added one click install with HACS link

## [1.0.2] - 2025-01-10
- Fix URLs for hotspot status and info data. Should've double checked this to before starting
- Removed redundant files

## [1.0.1] - 2025-01-10
- Hopefully this fixes the HACS not showing any information about the integration
- Other repo organization to make HACS validation work
- No code changes

## [1.0.0] - 2025-01-09

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
