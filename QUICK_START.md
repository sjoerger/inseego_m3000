# Inseego M3000 Home Assistant Integration - Quick Start

## 📦 What You Have

This is a complete, production-ready Home Assistant custom integration for the Inseego M3000 portable hotspot.

## 🚀 Installation Steps

1. **Copy to Home Assistant**
   ```
   Copy the entire 'inseego_m3000' folder to:
   <your-home-assistant-config>/custom_components/inseego_m3000/
   ```

2. **Restart Home Assistant**
   - Go to **Settings** → **System** → **Restart**

3. **Add the Integration**
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**
   - Search for "Inseego M3000"
   - Enter your hotspot's IP address (usually `192.168.1.1`)
   - Click Submit

## 📊 What You'll Get

### 24 Sensors
**Connection & Signal:**
- Signal Strength (0-5 bars)
- SNR (Signal to Noise Ratio)
- Network Provider
- Technology (4G/5G/5G UWB)
- Connection State
- IP Address

**Session Data:**
- Data Received/Transmitted/Total (bytes)
- Connection Duration
- Connected Clients (Total/WiFi/Primary)

**Billing Cycle Data:**
- Current Billing Cycle Usage (GB)
- Current Cycle Download/Upload (GB)
- Data Allowance (GB)
- Data Remaining (GB)
- Data Allowance Remaining (%)
- Days Until Cycle Reset
- Billing Cycle End Date

**Device Status:**
- Battery Percentage
- SIM Status
- GPS Status

### 8 Binary Sensors
- Connection Status
- WiFi Enabled
- Mobile Data Enabled
- Battery Charging
- Battery Present
- Ethernet Connected
- Airplane Mode
- Guest WiFi Enabled

## 📁 File Structure

```
inseego_m3000/
├── __init__.py              # Integration initialization
├── manifest.json            # Integration metadata
├── config_flow.py           # UI configuration
├── coordinator.py           # Data update coordinator
├── sensor.py                # Sensor entities
├── binary_sensor.py         # Binary sensor entities
├── const.py                 # Constants
├── strings.json             # UI strings
├── hacs.json               # HACS metadata
├── translations/
│   └── en.json             # English translations
├── README.md               # Main documentation
├── INSTALLATION.md         # Detailed installation guide
├── EXAMPLES.md             # Dashboard examples
└── CHANGELOG.md            # Version history
```

## 🔧 Key Features

1. **UI Configuration** - No YAML editing required
2. **Automatic Discovery** - All entities created automatically
3. **Efficient Polling** - Configurable update interval (10-300 seconds)
4. **Statistics Support** - Long-term data tracking for data usage
5. **Device Registry** - All entities grouped under one device
6. **Error Handling** - Comprehensive error handling and logging
7. **HACS Ready** - Can be distributed via HACS

## 📖 Documentation

- **README.md** - Full feature list and overview
- **INSTALLATION.md** - Step-by-step installation and troubleshooting
- **EXAMPLES.md** - Dashboard configurations and automations
- **CHANGELOG.md** - Version history and roadmap

## 🎯 Example Use Cases

### Monitor Signal Strength
Track your hotspot's signal quality over time and get alerts when it drops.

### Track Data Usage
Monitor data consumption and set alerts for usage thresholds.

### Battery Management
Get notifications when battery is low or charging status changes.

### Connection Monitoring
Know when your hotspot connects/disconnects from the network.

### Client Tracking
See how many devices are connected to your hotspot.

## 🛠️ Customization

All sensors support:
- Custom entity names
- Dashboard customization
- Statistics and history
- Automations and scripts
- Template sensors for advanced calculations

## 📝 Example Automation

```yaml
automation:
  - alias: "Hotspot Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inseego_m3000_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Hotspot battery is at {{ states('sensor.inseego_m3000_battery') }}%"
```

## 🐛 Troubleshooting

**Can't find the integration?**
- Make sure you've restarted Home Assistant after copying the files
- Check that the folder is in `custom_components/inseego_m3000/`

**"Cannot connect" error?**
- Verify the IP address (try `http://192.168.1.1/status_data.json` in a browser)
- Ensure Home Assistant can reach the hotspot's network
- Check that the hotspot is powered on

**Entities not updating?**
- Check the scan interval setting
- Review Home Assistant logs for errors
- Try reloading the integration

## 📞 Support

For issues or questions:
1. Check INSTALLATION.md for detailed troubleshooting
2. Review Home Assistant logs
3. Open an issue on GitHub with relevant details

## 🎉 Next Steps

1. Install the integration
2. Add some entities to your dashboard (see EXAMPLES.md)
3. Create automations for monitoring
4. Enjoy having your hotspot integrated into Home Assistant!

---

**Version:** 1.0.0  
**Compatible with:** Home Assistant 2024.1.0+  
**License:** MIT
