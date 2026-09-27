---
title: When something goes wrong
nav_order: 8
---

# When something goes wrong

Each section starts with what you see, then what it means and what to do.

## The log says "No credentials configured — cannot connect"

The plugin has no EcoFlow email and password.

- Fill in **EcoFlow Email** and **EcoFlow Password** in **Plugins → EcoFlow Cloud → Configure**, or put both in `IndigoSecrets.py` as the [Settings](settings.md) page shows.

## The log says "Login failed" or "Authentication failed"

EcoFlow did not accept the sign-in, or could not be reached.

- Check the email and password by signing in to the EcoFlow app with them.
- Check **API Server** is the region your EcoFlow account belongs to.
- Check the Mac that runs Indigo can reach the internet.

The plugin tries again once a minute by itself.

## The log says "No configured devices — MQTT not started"

The plugin has nothing to listen for, because no power station has been added, or every one is disabled or has no serial number.

- Add a power station as [Getting started](getting-started.md) shows, then choose **Plugins → EcoFlow Cloud → Reconnect to EcoFlow Cloud**.

## A new power station never comes online

The plugin was already connected when you added it, so it is not listening for it yet.

- Choose **Plugins → EcoFlow Cloud → Reconnect to EcoFlow Cloud**. Do the same after changing a serial number.
- Check the **Serial Number** matches the one the EcoFlow app shows under **Device Info**, character for character.
- Check you chose the right model, **EcoFlow River 3** or **EcoFlow Delta 3**, when you made the device.

## The log says a power station is "offline - no message for >600s"

No reading has come from that power station for 10 minutes.

- Check the power station is switched on, on Wi-Fi, and shows as online in the EcoFlow app.
- If the power station has switched itself off, have a look at its standby timer, which **Set Device Standby Timer** can change.

When readings start again, **Device Online** turns True by itself and the log says the power station is online.

## An action does nothing, and the log says it was skipped

The log line says why:

- **device offline** — the power station is not sending readings, so the plugin does not send it commands. See the section above.
- **MQTT not connected** — the plugin is not connected to EcoFlow. Choose **Reconnect to EcoFlow Cloud**, and read the log for the reason if it does not connect.
- **no serial number configured** — open the device and fill in **Serial Number**.

If the log says **command send FAILED**, the plugin could not send the command to EcoFlow. Try again, and choose **Reconnect to EcoFlow Cloud** if it keeps failing.

## The log says "Protobuf import failed"

The plugin's add-on libraries are missing. Indigo fetches them the first time the plugin starts, which needs an internet connection.

- Check the Mac can reach the internet, then restart the plugin with **Plugins → EcoFlow Cloud → Reload**.

## Battery capacity looks far too big

Versions before 1.9 showed the capacity in milliamp-hours while calling it watt-hours, so a Delta 3 read 20000 Wh. Install the latest version from the [Releases page](https://github.com/Highsteads/EcoFlowCloud/releases/latest).

## Still stuck?

Choose **Plugins → EcoFlow Cloud → Show Plugin Info**, copy the lines it writes to the Event Log, and post them on the [Indigo forum](https://forums.indigodomo.com) with a description of what you see. You can also [raise an issue on GitHub](https://github.com/Highsteads/EcoFlowCloud/issues). I no longer have any EcoFlow power stations, so I cannot test a fix myself.
