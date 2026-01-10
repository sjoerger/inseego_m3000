# Example Dashboard Configuration

Here are some example Lovelace dashboard cards you can use to display your Inseego M3000 data.

## Simple Status Card

```yaml
type: entities
title: Hotspot Status
entities:
  - entity: binary_sensor.inseego_m3000_connection
    name: Connection
  - entity: sensor.inseego_m3000_network
    name: Network
  - entity: sensor.inseego_m3000_technology
    name: Technology
  - entity: sensor.inseego_m3000_signal_strength
    name: Signal
  - entity: sensor.inseego_m3000_battery
    name: Battery
```

## Billing Cycle Card

```yaml
type: entities
title: Data Usage This Month
entities:
  - entity: sensor.inseego_m3000_current_billing_cycle_usage
    name: Total Used
  - entity: sensor.inseego_m3000_data_allowance
    name: Monthly Allowance
  - entity: sensor.inseego_m3000_data_remaining
    name: Remaining
  - entity: sensor.inseego_m3000_data_allowance_remaining
    name: Percent Remaining
  - entity: sensor.inseego_m3000_days_until_cycle_reset
    name: Days Left
  - entity: sensor.inseego_m3000_billing_cycle_end_date
    name: Cycle Ends
```

## Billing Usage Gauge

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

## Detailed Info Card

```yaml
type: entities
title: Hotspot Details
entities:
  - type: section
    label: Connection
  - entity: sensor.inseego_m3000_network
  - entity: sensor.inseego_m3000_technology
  - entity: sensor.inseego_m3000_signal_strength
  - entity: sensor.inseego_m3000_snr
  - entity: sensor.inseego_m3000_connection_duration
  - type: section
    label: Session Data Usage
  - entity: sensor.inseego_m3000_total_data_usage
  - entity: sensor.inseego_m3000_data_received
  - entity: sensor.inseego_m3000_data_transmitted
  - type: section
    label: Billing Cycle
  - entity: sensor.inseego_m3000_current_billing_cycle_usage
  - entity: sensor.inseego_m3000_data_allowance
  - entity: sensor.inseego_m3000_data_remaining
  - entity: sensor.inseego_m3000_data_allowance_remaining
  - entity: sensor.inseego_m3000_billing_cycle_end_date
  - type: section
    label: Clients
  - entity: sensor.inseego_m3000_connected_clients
  - entity: sensor.inseego_m3000_wifi_clients
  - entity: sensor.inseego_m3000_primary_clients
  - type: section
    label: Power
  - entity: sensor.inseego_m3000_battery
  - entity: binary_sensor.inseego_m3000_battery_charging
```

## Gauge Cards

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.inseego_m3000_signal_strength
    name: Signal Strength
    min: 0
    max: 5
    severity:
      green: 3
      yellow: 2
      red: 0
  - type: gauge
    entity: sensor.inseego_m3000_battery
    name: Battery
    min: 0
    max: 100
    severity:
      green: 50
      yellow: 20
      red: 0
```

## Data Usage Statistics Card

```yaml
type: statistic
entity: sensor.inseego_m3000_total_data_usage
period:
  calendar:
    period: month
stat_type: change
name: Monthly Data Usage
```

## Mini Graph Cards

```yaml
type: vertical-stack
cards:
  - type: custom:mini-graph-card
    entities:
      - entity: sensor.inseego_m3000_signal_strength
    name: Signal Strength History
    hours_to_show: 24
    points_per_hour: 4
    line_color: blue
    line_width: 2
    
  - type: custom:mini-graph-card
    entities:
      - entity: sensor.inseego_m3000_battery
    name: Battery History
    hours_to_show: 24
    points_per_hour: 4
    line_color: green
    line_width: 2
```

## Grid Dashboard Layout

```yaml
type: grid
columns: 2
square: false
cards:
  - type: entity
    entity: binary_sensor.inseego_m3000_connection
    name: Connection Status
    
  - type: entity
    entity: sensor.inseego_m3000_network
    name: Network
    
  - type: entity
    entity: sensor.inseego_m3000_technology
    name: Technology
    
  - type: entity
    entity: sensor.inseego_m3000_signal_strength
    name: Signal
    
  - type: entity
    entity: sensor.inseego_m3000_battery
    name: Battery
    
  - type: entity
    entity: sensor.inseego_m3000_connected_clients
    name: Clients
```

## Markdown Card with Multiple Sensors

```yaml
type: markdown
content: >
  ## 📡 Hotspot Status


  **Network:** {{ states('sensor.inseego_m3000_network') }} ({{
  states('sensor.inseego_m3000_technology') }})

  **Signal:** {{ states('sensor.inseego_m3000_signal_strength') }} bars |
  SNR: {{ states('sensor.inseego_m3000_snr') }} dB

  **Battery:** {{ states('sensor.inseego_m3000_battery') }}% {% if
  is_state('binary_sensor.inseego_m3000_battery_charging', 'on') %}🔌{%
  endif %}


  **Clients:** {{ states('sensor.inseego_m3000_connected_clients') }}
  connected

  **Data Used:** {{ (states('sensor.inseego_m3000_total_data_usage') | float /
  1024 / 1024 / 1024) | round(2) }} GB
title: Inseego M3000
```

## Billing Cycle Progress Card

```yaml
type: markdown
content: >
  ## 📊 Billing Cycle


  **Used:** {{ states('sensor.inseego_m3000_current_billing_cycle_usage') }} GB
  of {{ states('sensor.inseego_m3000_data_allowance') }} GB

  **Remaining:** {{ states('sensor.inseego_m3000_data_remaining') }} GB ({{
  states('sensor.inseego_m3000_data_allowance_remaining') }}%)

  **Download:** {{ states('sensor.inseego_m3000_current_cycle_download') }} GB
  | **Upload:** {{ states('sensor.inseego_m3000_current_cycle_upload') }} GB


  **Cycle ends:** {{ states('sensor.inseego_m3000_billing_cycle_end_date') }}
  ({{ states('sensor.inseego_m3000_days_until_cycle_reset') }} days left)
title: Data Usage This Month
```

## Conditional Card (Show Warning on Low Battery)

```yaml
type: conditional
conditions:
  - entity: sensor.inseego_m3000_battery
    state_not: unavailable
  - condition: numeric_state
    entity: sensor.inseego_m3000_battery
    below: 20
card:
  type: markdown
  content: ⚠️ **Low Battery:** {{ states('sensor.inseego_m3000_battery') }}%
```

## Full Dashboard Example

```yaml
title: Hotspot Monitor
views:
  - title: Overview
    path: overview
    cards:
      - type: markdown
        content: >
          ## 📡 Inseego M3000 Hotspot
        
      - type: horizontal-stack
        cards:
          - type: gauge
            entity: sensor.inseego_m3000_signal_strength
            name: Signal
            min: 0
            max: 5
          - type: gauge
            entity: sensor.inseego_m3000_battery
            name: Battery
            
      - type: entities
        title: Connection Details
        entities:
          - entity: binary_sensor.inseego_m3000_connection
          - entity: sensor.inseego_m3000_network
          - entity: sensor.inseego_m3000_technology
          - entity: sensor.inseego_m3000_ip_address
          
      - type: entities
        title: Data Usage
        entities:
          - entity: sensor.inseego_m3000_total_data_usage
          - entity: sensor.inseego_m3000_data_received
          - entity: sensor.inseego_m3000_data_transmitted
          
      - type: entities
        title: Connected Devices
        entities:
          - entity: sensor.inseego_m3000_connected_clients
          - entity: sensor.inseego_m3000_wifi_clients
          - entity: sensor.inseego_m3000_primary_clients
```

## Useful Template Sensors

Add these to your `configuration.yaml` to create additional helpful sensors:

```yaml
template:
  - sensor:
      - name: "Hotspot Data Usage GB"
        unit_of_measurement: "GB"
        state: >
          {{ (states('sensor.inseego_m3000_total_data_usage') | float / 1024 / 1024 / 1024) | round(2) }}
        
      - name: "Hotspot Uptime"
        state: >
          {% set duration = states('sensor.inseego_m3000_connection_duration') | int %}
          {% set hours = (duration / 3600) | int %}
          {% set minutes = ((duration % 3600) / 60) | int %}
          {{ hours }}h {{ minutes }}m
```

## Notes

- Replace `192.168.1.1` with your actual hotspot IP if different
- Some cards require custom Lovelace cards (like mini-graph-card)
- Install custom cards through HACS for best experience
- Adjust colors, thresholds, and layouts to your preference
