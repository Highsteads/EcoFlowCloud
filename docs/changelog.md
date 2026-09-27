---
title: Version history
nav_order: 9
---

# Version history

The newest version is at the top.

## 1.11 — 27 September 2026

- **A new power station is picked up straight away.** When you add a power station, switch one back on or change its serial number, the plugin starts listening for it as soon as you click Save. Before, it only listened for the power stations it knew about when it connected, so you had to choose **Reconnect to EcoFlow Cloud** first.
- **`IndigoSecrets.py` can hold just one of the two EcoFlow lines.** The plugin used to ignore the file unless it held both the email and the password. It now reads each on its own and takes the other from the **Configure** window.
- The blank `IndigoSecrets_example.py` inside the plugin now has the two EcoFlow lines, ready to fill in.
- The plugin's author is shown as CliveS & Claude.

## 1.10 — 8 August 2026

The **About** item in the Plugins menu opens this project's page. It went nowhere before. Nothing else changed.

## 1.9 — 4 July 2026

- **Battery capacity reads in true watt-hours.** The power stations report their remaining, full and design capacity in milliamp-hours, and the plugin had been showing those figures as watt-hours, so a River 3 Max read 12800 Wh and a Delta 3 20000 Wh. They are now converted, so a River 3 Max reads about 573 Wh and a Delta 3 about 1024 Wh.
- A blank or non-numeric value in an action or a setting no longer stops that action from running.

## 1.8 — 19 June 2026

Readings refresh every 10 seconds instead of every 30.

## 1.7 — 19 June 2026

The plugin connected but then showed no live data. The River 3 and Delta 3 only send their readings when asked, so the figures froze at their last values. The plugin now asks each power station for its readings as soon as it connects and at regular intervals after that, so the battery level, solar input and power flow stay live.

## 1.6 — 10 June 2026

Behind-the-scenes checks on the code, run each time it changes. Nothing changed in how the plugin behaves.

## 1.5 — 5 June 2026

- Changing a device's serial number restarts that device, as 1.4 intended. That restart had been switched off by mistake.
- Opening **Configure** no longer copies the email and password from `IndigoSecrets.py` into the plugin's saved settings.
- The Delta 3's **Charging State** shows charging, discharging or idle correctly.

## 1.4 — 25 May 2026

Only a change to a device's serial number restarts that device. Ticking or unticking **Mirror Key States to Variables** no longer does.

## 1.3 — 23 May 2026

Every log line starts with the time to the thousandth of a second, with a menu item, **Toggle Timestamps in Log (on/off)**, to turn that off.

## 1.2 — 15 May 2026

Fixed an occasional warning when copying readings into Indigo variables, which happened when two power stations tried to make the same variable at the same moment.

## 1.1 — 11 May 2026

- **Set AC Output**, **Set DC Output**, **Set AC Charging Power**, **Set Max Charge Level** and **Set Min Discharge Level** work. In 1.0 they did nothing, and only **Set XBoost Mode** worked.
- New actions: **Set Buzzer**, **Set LCD Brightness**, **Set Screen Timeout** and **Set Device Standby Timer**.
- New readings: firmware versions, fault numbers, fan level, mains output frequency, sleep state, the low power alarm, the buzzer and timer settings, the second USB-C and DC ports, and the running energy totals, which now come through on the Delta 3 as well as the River 3.
- An action that fails to send is logged as an error rather than a warning.

## 1.0 — 10 May 2026

First release, for the EcoFlow River 3 and Delta 3 through EcoFlow's cloud.
