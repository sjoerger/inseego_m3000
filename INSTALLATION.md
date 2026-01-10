# Installation Guide for Inseego M3000 Integration

## Quick Start

### Step 1: Install the Integration

**Option A: HACS (Recommended)**
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the menu (three dots) → "Custom repositories"
4. Add your repository URL
5. Select "Integration" as category
6. Find "Inseego M3000 Hotspot" and click "Download"
7. Restart Home Assistant

**Option B: Manual Installation**
1. Download the `inseego_m3000` folder
2. Copy it to `<config>/custom_components/inseego_m3000`
3. Your directory structure should look like:
   ```
   custom_components/
   └── inseego_m3000/
       ├── __init__.py
       ├── manifest.json
       ├── config_flow.py
       ├── coordinator.py
       ├── sensor.py
       ├── binary_sensor.py
       ├── const.py
       └── translations/
           └── en.json
   ```
4. Restart Home Assistant

### Step 2: Configure the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "Inseego M3000"
4. Enter your configuration:
   - **Host**: The IP address of your hotspot (usually `192.168.1.1`)
   - **Scan Interval**: How often to update (default: 30 seconds)
5. Click **Submit**

### Step 3: Verify Installation

1. Go to **Settings** → **Devices & Services**
2. Find "Inseego M3000 Hotspot" in your integrations
3. Click on it to see the device
4. Verify all sensors are showing data

## Finding Your Hotspot IP Address

Your Inseego M3000's IP address depends on how you're connected:

### WiFi Connection
- Default IP: **192.168.1.1**
- Check the hotspot's screen for the exact IP
- Look in your device's WiFi settings for the gateway address

### USB Connection
- May use a different IP range
- Check your computer's network settings for the gateway

### Ethernet Connection  
- Check your router's DHCP client list
- The device will appear as "Inseego M3000"

## Testing the API

Before installing, you can verify the API works:

1. Connect to your hotspot's WiFi
2. Open a browser and go to: `http://192.168.1.1/status_data.json`
3. You should see JSON data similar to the example provided
4. If you see the data, the integration will work!

## Common Issues

### "Cannot Connect" Error
- **Check IP Address**: Make sure you're using the correct IP
- **Network Access**: Ensure Home Assistant can reach the hotspot's network
- **Firewall**: Check if any firewall is blocking the connection
- **Device Power**: Verify the hotspot is powered on

### "Invalid Device" Error  
- The device at that IP is not an Inseego M3000
- The API endpoint might have changed (check firmware version)
- Try accessing the status page manually in a browser

### No Entities Showing Up
- Wait a few minutes after adding the integration
- Check **Settings** → **Devices & Services** → **Entities** tab
- Look for entities starting with `sensor.inseego_m3000_`
- Check the Home Assistant logs for errors

### Entities Not Updating
- Check the scan interval in integration options
- Verify the hotspot is still connected
- Check Home Assistant logs for API errors
- Try reloading the integration

## Advanced Configuration

### Changing Update Interval

1. Go to **Settings** → **Devices & Services**
2. Find "Inseego M3000 Hotspot"
3. Click **Configure**
4. Adjust the scan interval (10-300 seconds)
5. Click **Submit**

### Multiple Hotspots

You can add multiple Inseego M3000 devices:
1. Each must have a unique IP address
2. Add each one separately through the integration setup
3. They'll appear as separate devices in Home Assistant

## Next Steps

After installation:
1. **Add to Dashboard**: Add your favorite sensors to a Lovelace dashboard
2. **Create Automations**: Set up alerts for low battery, poor signal, etc.
3. **Monitor Usage**: Track your data usage over time
4. **Explore Features**: Check out all available sensors and binary sensors

## Getting Help

If you encounter issues:
1. Check the Home Assistant logs: **Settings** → **System** → **Logs**
2. Look for entries containing "inseego_m3000"
3. Report issues on GitHub with relevant log entries
4. Include your Home Assistant version and hotspot firmware version

## Uninstalling

To remove the integration:
1. Go to **Settings** → **Devices & Services**
2. Find "Inseego M3000 Hotspot"
3. Click the three dots → **Delete**
4. Confirm deletion
5. (Optional) Remove the custom_components folder if installed manually

Enjoy monitoring your Inseego M3000 hotspot with Home Assistant!
