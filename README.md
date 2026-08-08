# EcoFlow Cloud

> **Retired, July 2026.** The power stations were sold and the plugin came off my Indigo
> server on 6 July 2026, so nothing here is being run or watched any more. It worked well
> while I had the hardware, and it was still working the day it came off. The repo stays up
> as source for anyone who still has EcoFlow kit and wants a starting point, or a fork. Do
> not expect fixes from me — I have nothing left to test them against.

**Indigo home automation plugin.**

Indigo plugin: integrate EcoFlow portable power stations (Delta/River series) via the EcoFlow cloud API — battery SOC, solar input, charging state and per-device controls

**Author:** CliveS & Claude Sonnet 4.6
**Platform:** Indigo 2022.1 or later, macOS (Python 3.10+ bundled with Indigo)

*Developed and tested on Indigo 2025.2 / Python 3.13. Older Indigo releases that meet the minimum API version above should also work — the API floor is what Indigo's plugin loader actually checks.*
**Bundle ID:** `com.clives.indigoplugin.ecoflowcloud`
**Version:** 1.9

---

## Recent changes

**v1.10** — **Added the missing support link.** Every Indigo plugin is meant to carry a web address inside its bundle — it is what the "About" item in the Plugins menu opens. This one had no address at all, so that menu item went nowhere. It now points at this repository. Nothing else changed.
- **v1.9** — corrects the battery capacity readings. The Delta 3 and River 3 report their remaining, full and design capacity in milliamp-hours, but the plugin had been passing those figures straight through as watt-hours, so a 572 Wh River 3 Max read as "12800 Wh" and a 1024 Wh Delta 3 as "20000 Wh". They are now converted properly, so Battery Remaining, Full Capacity and Design Capacity all read in true watt-hours. The plugin is also a touch more robust — a blank or non-numeric value left in an action or a setting no longer stops that action from running.
- **v1.8** — readings now refresh every 10 seconds instead of every 30, so battery level, solar input and power flow track close to real time.
- **v1.7** — fixes the plugin connecting but then showing no live data. The River 3 and Delta 3 do not stream their readings on their own — they only send an update when they are asked for one, so the plugin sat on a silent connection and the figures slowly went stale until the next restart. It now asks each device for its latest readings the moment it connects and then on a short interval after, so battery level, solar input and power flow stay live. As a happy side effect, the estate watchdog no longer needs to restart the plugin every 12 hours.
- **v1.6** — internal tidy-up only. Added automated code linting and a continuous-integration test gate so regressions are caught before release. No change to how the plugin behaves.
- **v1.5** — three fixes from an estate-wide review. A device's serial-number change is now picked up properly (a lifecycle method had been accidentally disabled), the Configure dialog no longer writes your EcoFlow login back into the stored settings, and the Delta 3's charging/discharging state is reported correctly.
- **v1.4** — changing a device's serial number now re-establishes communication straight away rather than needing a plugin restart.
- **v1.3** — every log line now carries a millisecond timestamp, matching the other CliveS plugins.
- **v1.2** — fixed an intermittent warning when mirroring device readings into Indigo variables, caused by two devices trying to create the same variable at once.

---

## Installation

1. Go to the [Releases page](https://github.com/Highsteads/EcoFlowCloud/releases) and download `EcoFlowCloud.indigoPlugin.zip`
2. Unzip the downloaded file — you will get `EcoFlowCloud.indigoPlugin`
3. Double-click `EcoFlowCloud.indigoPlugin` — Indigo will install it automatically
4. In Indigo: **Plugins → Manage Plugins → Enable** EcoFlow Cloud
5. Open **Plugins → EcoFlow Cloud → Configure** and fill in any required fields

---

## Credentials — `IndigoSecrets.py` vs `IndigoSecrets_example.py`

This plugin, like every CliveS Indigo plugin, reads sensitive values from one
shared master file:

`/Library/Application Support/Perceptive Automation/IndigoSecrets.py`

| File | Purpose | Real data? | Committed to GitHub? |
|------|---------|------------|----------------------|
| `IndigoSecrets.py` | Working file the plugin reads at runtime. Keep a backup in a password manager. | YES | **NO** — listed in `.gitignore` |
| `IndigoSecrets_example.py` | Template only — empty placeholders. Shipped in the plugin bundle. | NO | YES |

If you don't have `IndigoSecrets.py`, copy `IndigoSecrets_example.py` out of
the plugin bundle into `/Library/Application Support/Perceptive Automation/`,
rename it to `IndigoSecrets.py`, and fill in your values. Or skip the file
altogether and type the values into the plugin's configuration dialog — where
both are set, `IndigoSecrets.py` wins.

If neither source supplies a value the plugin needs, it logs an ERROR naming
the key and telling you to either fill in the matching field or add the key to
`IndigoSecrets.py`.

---

## Logging

Every log line carries a millisecond timestamp `[HH:MM:SS.mmm]`, so you can
line events up precisely against the other CliveS plugins — Device Activity
Monitor uses the same format.

To turn the prefix off, or back on, at any time:

**Plugins → EcoFlow Cloud → Toggle Timestamps in Log (on/off)**

The plugin stores the setting in `pluginPrefs` (`timestampEnabled`) and it
survives a restart. It defaults to ON.

---

## Repository structure

```
README.md                        ← this file (GitHub displays this)
EcoFlowCloud.indigoPlugin/
├── Contents/
│   ├── Info.plist
│   └── Server Plugin/
│       ├── plugin.py
│       └── ...
└── Contents/Server Plugin/IndigoSecrets_example.py   ← credential template
```

## Authors & licence

Vibed into existence by **CliveS**, who knew what he wanted, argued until he got it, and tested it on a real house. Typed at inhuman speed by **Claude** (Anthropic), who mostly did as it was told.

© 2026 CliveS · [MIT licence](LICENSE) — copy it, fork it, bend it, break it, fix it, ship it. If it breaks, you get to keep both pieces.
