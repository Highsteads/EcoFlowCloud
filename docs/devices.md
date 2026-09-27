---
title: Your devices
nav_order: 3
---

# Your devices

Each power station you add becomes one Indigo device. There are two kinds:

| In Indigo | Your power station |
|---|---|
| **EcoFlow River 3** | A River 3 |
| **EcoFlow Delta 3** | A Delta 3 |

Both show the same readings, and the Delta 3 has one more, **AC Output Voltage**. The names below are the ones Indigo shows when you build a trigger or look at the device's states. A reading stays blank if your model never reports it.

## Battery

| Shown as | What it means |
|---|---|
| **Battery SOC (%)** | How full the battery is. SOC stands for state of charge. |
| **Battery Health (%)** | How much of its original capacity the battery still holds, as the power station reports it. |
| **Battery Remaining (Wh)** | The energy left in the battery, in watt-hours. |
| **Battery Full Capacity (Wh)** | How much the battery holds when full today, in watt-hours. |
| **Battery Design Capacity (Wh)** | How much the battery held when new, in watt-hours. |
| **Battery Voltage (V)** | The battery's voltage right now. |
| **Cell Temp Min (degC)** and **Cell Temp Max (degC)** | The coolest and warmest battery cells, in degrees Celsius. |
| **Charge Cycles** | How many full charge cycles the battery has been through. |
| **Charging State** | **charging**, **discharging** or **idle**. It shows **unknown** if the power station sends a value the plugin does not recognise. |

## Power coming in and going out

All in watts, as they are right now.

| Shown as | What it means |
|---|---|
| **Total Input Power (W)** | Everything coming in, from solar and the mains together. |
| **Total Output Power (W)** | Everything going out, across every socket. |
| **Solar Input (W)** | What is coming in from solar panels. |
| **AC Input (W)** | What is coming in from the mains. |
| **AC Output (W)** | What the mains sockets on the power station are supplying. |
| **AC Output Voltage (V)** | The voltage at the mains sockets. Delta 3 only. |
| **12V DC Output (W)** | What the 12 volt car-style socket is supplying. |
| **USB-C Output (W)** and **USB-C 2 Output (W)** | What each USB-C socket is supplying. |
| **USB-A 1 Output (W)** and **USB-A 2 Output (W)** | What each USB-A socket is supplying. |
| **DC Port Output (W)** and **DC Port 2 Output (W)** | The power on the power station's other DC ports, as it reports them. |
| **BMS Power (W)** | The power going into or out of the battery, as the battery's own management reports it. |

## Time left

| Shown as | What it means |
|---|---|
| **Time to Full (min)** | Minutes until the battery is full at the present rate of charge. |
| **Time Remaining (min)** | Minutes until the battery runs down at the present rate of use. |

## Temperatures

| Shown as | What it means |
|---|---|
| **DC Converter Temp (degC)** and **AC Converter Temp (degC)** | The temperature inside the power station's DC and AC circuits, in degrees Celsius. |
| **Fan Level** | The fan speed, as a number the power station reports. |

## The power station's own settings

These show how the power station is set, whether you changed a setting from Indigo, the EcoFlow app or the buttons on the unit. True means on and False means off.

| Shown as | What it means |
|---|---|
| **AC Output Enabled** | Whether the mains sockets are switched on. |
| **DC Output Enabled** | Whether the 12 volt DC output is switched on. |
| **XBoost Enabled** | Whether EcoFlow's XBoost feature is on. |
| **Max Charge Level (%)** | The level the power station stops charging at. |
| **Min Discharge Level (%)** | The lowest level the power station will run the battery down to. |
| **AC Charging Power (W)** | The most power the power station will take from the mains while charging. |
| **Buzzer Enabled** | Whether the power station beeps. |
| **Screen Timeout (s)** | Seconds before the screen turns off. |
| **AC Standby Timer (s)** and **Device Standby Timer (s)** | Seconds of no use before the mains sockets, or the whole power station, switch off. |
| **Sleep State** | The power station's sleep state, as a number it reports. |

## Running totals

These count up over the power station's life.

| Shown as | What it means |
|---|---|
| **AC Output Energy Total (Wh)** | Energy supplied through the mains sockets. |
| **AC Input Energy Total (Wh)** | Energy taken from the mains. |
| **Solar Input Energy Total (Wh)** | Energy taken from solar. |
| **12V DC Output Energy Total (Wh)** | Energy supplied through the 12 volt socket. |
| **USB-C Output Energy Total (Wh)** and **USB-A Output Energy Total (Wh)** | Energy supplied through the USB sockets. |
| **Device Working Time (s)** | How long the power station has been running, in seconds. |

## Faults and firmware

| Shown as | What it means |
|---|---|
| **Low Power Alarm** | True when the power station is raising its low battery alarm. |
| **AC Output Frequency (Hz)** | The frequency of the mains output. |
| **Error Code**, **BMS Error Code**, **PD Error Code**, **MPPT Error Code** and **Inverter Error Code** | The fault numbers the power station reports for itself and for each of its parts — the battery, the power board, the solar charger and the mains inverter. |
| **PD Firmware**, **IoT Firmware**, **MPPT Firmware**, **Inverter Firmware** and **BMS Firmware** | The firmware versions of each part, as numbers. |

## From the plugin

| Shown as | What it means |
|---|---|
| **Device Online** | True while readings are arriving. It is False when the plugin starts, until the first reading comes in, and turns False again if no reading arrives for 10 minutes. |
| **Last Update** | The time of the last reading, such as `14:05:32`. |

## Readings copied to variables

If you tick **Mirror Key States to Variables** in a device's settings, the plugin also writes these readings into Indigo variables, in a variable folder called **EcoFlow**, which it makes if you do not have one:

- Battery SOC, Total Input Power, Total Output Power, AC Output, Solar Input, Time Remaining and Charging State
- AC Output Enabled, DC Output Enabled, XBoost Enabled, Buzzer Enabled and Low Power Alarm, as True or False

Each variable is named `ecoflow_`, then the device's name, then the reading. Spaces and symbols in the device's name become underscores, and only the first 28 characters of the name are used, so a device called **Delta 3** gives variables such as `ecoflow_Delta_3_battery_soc` and `ecoflow_Delta_3_solar_in_w`.
