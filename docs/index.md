---
title: Home
nav_order: 1
---

# EcoFlow Cloud for Indigo

This plugin brings EcoFlow **River 3** and **Delta 3** portable power stations into [Indigo](https://www.indigodomo.com). It signs in to your EcoFlow account, the same one the EcoFlow app uses, and shows each power station's battery, solar input and power flow as an Indigo device, with actions to switch its outputs and change its charge settings.

Everything goes through EcoFlow's own servers, the same way the EcoFlow app does, so the Mac that runs Indigo needs to reach the internet and each power station needs to be on Wi-Fi and showing in the EcoFlow app.

I ran it with my own Delta 3 and River 3 power stations until I sold them, and it was working the day it came off my Indigo server in July 2026. I no longer have any EcoFlow kit, so I cannot test changes, but the plugin stays here for anyone who has.

## What it does for you

- **Shows each power station in Indigo** — how full the battery is, what is coming in from solar and the mains, what is going out of each socket, and how long until it is full or empty.
- **Refreshes every 10 seconds** by asking each power station for its latest readings.
- **Switches the AC and DC outputs** on and off from a schedule, a trigger or an action group.
- **Changes the power station's settings** — the charge limit, the lowest level it will run down to, the mains charging power, XBoost, the buzzer, the screen and the standby timer.
- **Tells you when a power station goes quiet**, marking it offline after 10 minutes without a reading.
- **Copies the main readings into Indigo variables** if you ask it to, for use on control pages and in scripts.

## Where to go next

| If you want to... | Read |
|---|---|
| Install the plugin and add your first power station | [Getting started](getting-started.md) |
| Know what each reading means | [Your devices](devices.md) |
| Understand what the plugin is doing behind the scenes | [How it works](how-it-works.md) |
| Control a power station from triggers, schedules and action groups | [Actions and triggers](actions-and-triggers.md) |
| Know what every setting does | [Settings](settings.md) |
| Know what each item in the Plugins menu does | [The plugin menu](plugin-menu.md) |
| Sort out a problem | [When something goes wrong](troubleshooting.md) |
| See what changed in each version | [Version history](changelog.md) |

## Download

The latest version is always on the [Releases page](https://github.com/Highsteads/EcoFlowCloud/releases/latest).
