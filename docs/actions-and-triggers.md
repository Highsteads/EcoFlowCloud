---
title: Actions and triggers
nav_order: 5
---

# Actions and triggers

## Actions

The plugin adds these actions, which you can use in a schedule, a trigger or an action group. Add an action, choose the one you want from the **EcoFlow Cloud** actions, and pick the power station it should change.

| Action | What it does | Choices |
|---|---|---|
| **Set AC Output** | Switches the mains sockets on or off. | Turn On, Turn Off |
| **Set DC Output** | Switches the 12 volt DC output on or off. | Turn On, Turn Off |
| **Set XBoost Mode** | Turns EcoFlow's XBoost feature on or off. | Enable, Disable |
| **Set Max Charge Level** | Sets the level the power station stops charging at. | 50%, 60%, 70%, 80%, 90% or 100% |
| **Set Min Discharge Level** | Sets the lowest level the power station will run the battery down to. | 0%, 5%, 10%, 15%, 20% or 30% |
| **Set AC Charging Power** | Sets the most power the power station takes from the mains while charging. | 50, 100, 150, 200, 250 or 305 watts |
| **Set Buzzer** | Turns the power station's beeps on or off. | Enable, Disable |
| **Set LCD Brightness** | Sets how bright the screen is. | Off, 20%, 40%, 50%, 60%, 80% or 100% |
| **Set Screen Timeout** | Sets how long the screen stays on. | Never, 30 seconds, 1, 2, 5, 10 or 30 minutes |
| **Set Device Standby Timer** | Sets how long the power station waits, unused, before switching itself off. | Never, 15 or 30 minutes, 1, 2 or 4 hours |

An action is only sent when the power station shows **Device Online** and the plugin is connected to EcoFlow. If either is not the case, the Event Log says the action was skipped and why. When an action is sent, the Event Log records it, such as `AC output -> on`.

The power station's own states, such as **AC Output Enabled** or **Max Charge Level (%)**, show the new setting once it sends its next reading.

## Triggers

The plugin has no triggers of its own. Every reading on the [Your devices](devices.md) page can start one of Indigo's ordinary **Device State Changed** triggers, so you can have Indigo act when something changes.

For example:

- When **Battery SOC (%)** falls below 20, send yourself a notification.
- When **Low Power Alarm** becomes True, switch off whatever the power station is running.
- When **Device Online** becomes False, tell you the power station has gone quiet.
- When **Solar Input (W)** rises above a level you choose, use **Set AC Output** to switch the mains sockets on.
