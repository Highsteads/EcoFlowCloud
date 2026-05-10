# EcoFlow Cloud

**Indigo home automation plugin.**

Indigo plugin: integrate EcoFlow portable power stations (Delta/River series) via the EcoFlow cloud API — battery SOC, solar input, charging state and per-device controls

**Author:** CliveS & Claude Sonnet 4.6
**Platform:** Indigo 2025.2 or later, macOS, Python 3.13
**Bundle ID:** `com.clives.indigoplugin.ecoflowcloud`
**Version:** 1.0

---

## Installation

1. Go to the [Releases page](https://github.com/Highsteads/EcoFlowCloud/releases) and download `EcoFlowCloud.indigoPlugin.zip`
2. Unzip the downloaded file — you will get `EcoFlowCloud.indigoPlugin`
3. Double-click `EcoFlowCloud.indigoPlugin` — Indigo will install it automatically
4. In Indigo: **Plugins → Manage Plugins → Enable** EcoFlow Cloud
5. Open **Plugins → EcoFlow Cloud → Configure** and fill in any required fields

---

## Credentials — `IndigoSecrets.py` vs `IndigoSecrets_example.py`

This plugin (along with all CliveS Indigo plugins) reads sensitive values from
a shared master credentials file at:

`/Library/Application Support/Perceptive Automation/IndigoSecrets.py`

| File | Purpose | Real data? | Committed to GitHub? |
|------|---------|------------|----------------------|
| `IndigoSecrets.py` | Working file the plugin reads at runtime. Keep a backup in a password manager. | YES | **NO** — listed in `.gitignore` |
| `IndigoSecrets_example.py` | Template only — empty placeholders. Shipped in the plugin bundle. | NO | YES |

If you do not have `IndigoSecrets.py`, copy `IndigoSecrets_example.py` from
the plugin bundle to that location and fill in your values. Or skip
`IndigoSecrets.py` entirely and enter values via the plugin's configuration
dialog — `IndigoSecrets.py` wins over the dialog when both are set.

If a required value is set in NEITHER source the plugin logs an ERROR
pointing the user to either fill in the matching field or add the key to
`IndigoSecrets.py`.

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

---

## License

GPL-3.0 — see plugin source files for details.
