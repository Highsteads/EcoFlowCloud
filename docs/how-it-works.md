---
title: How it works
nav_order: 4
---

# How it works

You do not need to know any of this to use the plugin. It is here for anyone who likes to know what is going on.

## Through EcoFlow's servers

The River 3 and Delta 3 do not talk to anything on your home network. They talk to EcoFlow's servers on the internet, and the EcoFlow app talks to the same servers. The plugin does what the app does.

1. **It signs in** to EcoFlow with your email and password, at the region you chose in **API Server**.
2. **It collects a separate key** from EcoFlow for EcoFlow's message service, which is how the power stations send their readings and receive commands.
3. **It connects to that service** over an encrypted connection, and listens for each power station whose serial number you have given it.

When you add a power station, switch one back on or change a serial number, the plugin starts listening for it straight away, without dropping the connection for the others. It stops listening for a serial number you have changed.

## Asking every 10 seconds

These power stations do not send their readings unless something asks for them. So as soon as the plugin connects, and every 10 seconds after, it asks each power station for its latest readings, and each one answers straight away through EcoFlow's servers. The plugin then brings the Indigo device up to date and sets **Last Update** to the time.

If no reading arrives from a power station for 10 minutes, the plugin sets its **Device Online** state to False and writes a warning in the Event Log. When readings start again, it sets it back to True and says so.

## If the connection drops

If the connection to EcoFlow drops, or signing in fails, the plugin tries again once a minute until it gets back in. You do not need to do anything, though **Reconnect to EcoFlow Cloud** in the Plugins menu makes it try straight away.

If you change your email, password or server in **Configure**, the plugin reconnects as soon as you click Save.

## Sending commands

An action such as **Set AC Output** goes the same way in reverse: from the plugin to EcoFlow's servers and on to the power station. The plugin only sends it when the power station is showing **Device Online** and the connection to EcoFlow is up, otherwise it writes a warning in the log and does nothing. The device's states show the change once the power station sends its next reading.

## Battery capacity in watt-hours

The power stations report their battery capacity in milliamp-hours. The plugin turns those figures into watt-hours using the voltage each model's battery is rated at — 51.2 volts for the Delta 3 and 44.8 volts for the River 3 — so a Delta 3 reads about 1024 Wh and a River 3 Max about 573 Wh. The plugin uses the rated voltage rather than the live one, so the capacity figures stay steady as the battery charges and empties.

## Your EcoFlow sign-in

The plugin reads your email and password from the shared `IndigoSecrets.py` file if you have one, otherwise from its **Configure** window. It looks for each on its own, so the file can hold just one of them and the other comes from the window. Where both have a value, the file wins. The [Settings](settings.md) page explains the file.
