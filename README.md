# EcoFlow Cloud for Indigo

**Watch and control EcoFlow River 3 and Delta 3 power stations from Indigo, through your EcoFlow account.**

**Version:** 1.10 | **Author:** CliveS & Claude | **Needs:** Indigo 2022.1 or later and an EcoFlow account

**[Read the full guide](https://highsteads.github.io/EcoFlowCloud/)** — setting up, what everything means, and what to do when something goes wrong.

---

## What it does

This plugin lets [Indigo](https://www.indigodomo.com) show and control EcoFlow portable power stations. It signs in to your EcoFlow account, the same one the EcoFlow app uses, and reaches each power station through EcoFlow's servers, so the Mac that runs Indigo needs to reach the internet.

- **Shows each power station as an Indigo device** — how full the battery is, solar and mains input, what each socket is supplying, and how long until it is full or empty.
- **Refreshes every 10 seconds** by asking each power station for its latest readings.
- **Switches the AC and DC outputs** on and off from a schedule, a trigger or an action group.
- **Changes the power station's settings** — the charge limit, the lowest level it will run down to, the mains charging power, XBoost, the buzzer, the screen and the standby timer.
- **Marks a power station offline** after 10 minutes without a reading, with a warning in the Event Log.
- **Copies the main readings into Indigo variables** if you tick a box, for use on control pages and in scripts.

I ran it with my own Delta 3 and River 3 power stations until I sold them, and it was working the day it came off my Indigo server in July 2026. I no longer have any EcoFlow kit, so I cannot test changes, but the plugin stays here for anyone who has.

## Which power stations it works with

| In Indigo | Your power station |
|---|---|
| **EcoFlow River 3** | A River 3 |
| **EcoFlow Delta 3** | A Delta 3 |

## Installing

1. Go to the [Releases page](https://github.com/Highsteads/EcoFlowCloud/releases/latest) and download `EcoFlowCloud.indigoPlugin.zip`
2. Unzip the downloaded file — you will get `EcoFlowCloud.indigoPlugin`
3. Double-click `EcoFlowCloud.indigoPlugin` — Indigo will install it automatically

## Setting it up

1. Open **Plugins → EcoFlow Cloud → Configure**, fill in the **EcoFlow Email** and **EcoFlow Password** you use in the EcoFlow app, set **API Server** to your account's region, and click **Save**.
2. Create a **New Device**, choose **EcoFlow Cloud** and the model, and type in the power station's **Serial Number**, which the EcoFlow app shows under **Device Info**.
3. Choose **Plugins → EcoFlow Cloud → Reconnect to EcoFlow Cloud**, and within a few seconds the device should show **Device Online** and fill in its readings.

The [full guide](https://highsteads.github.io/EcoFlowCloud/) goes through each step, explains every reading and setting, and covers what to do if something does not work.

## What's new

**v1.10** — The **About** item in the Plugins menu opens this project's page. It went nowhere before. Nothing else changed.

**v1.9** — Battery capacity reads in true watt-hours. It had been showing milliamp-hours, so a Delta 3 read 20000 Wh instead of about 1024 Wh. A blank value in an action or a setting no longer stops that action from running.

**v1.8** — Readings refresh every 10 seconds instead of every 30.

Every version is listed in the [version history](https://highsteads.github.io/EcoFlowCloud/changelog.html).

## Authors & licence

Vibed into existence by **CliveS**, who knew what he wanted, argued until he got it, and tested it on a real house. Typed at inhuman speed by **Claude** (Anthropic), who mostly did as it was told.

© 2026 CliveS · [MIT licence](LICENSE) — copy it, fork it, bend it, break it, fix it, ship it. If it breaks, you get to keep both pieces.
