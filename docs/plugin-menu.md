---
title: The plugin menu
nav_order: 7
---

# The plugin menu

These are under **Plugins → EcoFlow Cloud**.

| Menu item | What it does |
|---|---|
| **Reconnect to EcoFlow Cloud** | Drops the connection to EcoFlow, signs in again and reconnects straight away. Use it after adding a power station or changing a serial number, as the plugin only listens for the power stations it knows about when it connects. |
| **Log Device Status Summary** | Writes one line per power station to the Event Log, showing whether it is online, its serial number, its battery level, the power going in and out, and when the last reading arrived. A last line says whether the plugin is connected to EcoFlow and which server it uses. |
| **Toggle Timestamps in Log (on/off)** | Every line the plugin writes to the log starts with the time to the thousandth of a second, which helps when lining events up. This turns that on or off. It stays as you leave it. |
| **Show Plugin Info** | Writes the plugin's version and details of your Mac and Indigo to the log, along with which EcoFlow server it uses and whether an email and password are set. It never writes the email or password themselves, which makes it useful to include if you ask for help on the Indigo forum. |

**Log Device Status Summary** writes out each serial number, so take those out before you post its lines anywhere public.
