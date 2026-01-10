# Inseego M3000 Hotspot Integration

Monitor your Inseego M3000 portable hotspot directly in Home Assistant!

## What You Get

### 24 Sensors
- **Signal & Connection:** Signal strength, SNR, network type, technology (4G/5G/5G UWB)
- **Session Data:** Real-time bytes sent/received, connection duration
- **Billing Cycle:** Monthly usage, allowance, remaining data, cycle end date
- **Device Status:** Battery level, IP address, SIM status, GPS status
- **Connected Devices:** Total clients, WiFi clients, primary clients

### 8 Binary Sensors
- Connection status
- WiFi enabled
- Mobile data enabled
- Battery charging
- Battery present
- Ethernet connected
- Airplane mode
- Guest WiFi enabled

## Quick Setup

1. Install via HACS
2. Restart Home Assistant
3. Go to Settings → Devices & Services
4. Click Add Integration
5. Search for "Inseego M3000"
6. Enter your hotspot's IP address (usually `192.168.1.1`)
7. Done! All sensors will be created automatically

## Use Cases

### 📊 Monitor Data Usage
Track your monthly data consumption and get alerts before hitting your cap.

### 🔋 Battery Monitoring
Keep an eye on battery level and charging status.

### 📡 Signal Quality
Monitor signal strength and connection quality over time.

### 👥 Connected Devices
See how many devices are connected to your hotspot.

## Example Automation

Get notified when you've used 80% of your data allowance:

```yaml
automation:
  - alias: "Data Usage Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_data_allowance_remaining
        below: 20  # 20% remaining
    action:
      - service: notify.mobile_app
        data:
          message: "Warning: Only {{ states('sensor.inseego_m3000_data_remaining') }} GB remaining!"
```

## Dashboard Example

Create a comprehensive hotspot monitoring dashboard:

```yaml
type: entities
title: Hotspot Monitor
entities:
  - sensor.inseego_m3000_network
  - sensor.inseego_m3000_signal_strength
  - sensor.inseego_m3000_battery
  - sensor.inseego_m3000_current_billing_cycle_usage
  - sensor.inseego_m3000_data_allowance_remaining
  - sensor.inseego_m3000_connected_clients
```

## Requirements

- Inseego M3000 portable hotspot
- Network connectivity between Home Assistant and the hotspot
- Home Assistant 2024.1.0 or newer

## Support

- [Documentation](https://github.com/sjoerger/inseego_m3000)
- [Report Issues](https://github.com/sjoerger/inseego_m3000/issues)
- [Feature Requests](https://github.com/sjoerger/inseego_m3000/issues)
