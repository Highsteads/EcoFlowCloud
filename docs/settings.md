---
title: Settings
nav_order: 6
---

# Settings

## The plugin's settings

Open these with **Plugins → EcoFlow Cloud → Configure**. They apply to every power station.

| Setting | What it does |
|---|---|
| **EcoFlow Email** | The email address you use to sign in to the EcoFlow app. |
| **EcoFlow Password** | The password you use to sign in to the EcoFlow app. |
| **API Server** | Which of EcoFlow's regional servers holds your account: **EU / UK**, **US** or **Asia-Pacific**. EU / UK is chosen to start with. Choose **Custom...** only if EcoFlow gives you a different server. |
| **Custom API Host** | Only shown when **API Server** is set to **Custom...**. Type the server's name alone, such as `api-e.ecoflow.com`, without `https://` in front. |
| **Log Level** | How much the plugin writes to the Event Log: **Detailed Debugging**, **Debugging**, **Informational (default)**, **Warnings Only** or **Errors Only**. Leave it on Informational unless you are chasing a problem. |

The window will not save without an email and a password, unless the missing one is in `IndigoSecrets.py`. If you change the email, password or server, the plugin signs in again as soon as you click **Save**.

### Keeping your EcoFlow sign-in in one file

If you run several of my plugins, you can keep your passwords and keys in one shared file instead of typing them into each plugin. The file is called `IndigoSecrets.py` and lives in `/Library/Application Support/Perceptive Automation/`.

1. A blank copy, `IndigoSecrets_example.py`, comes inside the plugin. Copy it to `/Library/Application Support/Perceptive Automation/` and rename the copy `IndigoSecrets.py`. If you already have an `IndigoSecrets.py` from another of my plugins, use that one instead.
2. Find the two EcoFlow lines in the file and put your own email and password between the quotes. If your file came from another of my plugins and has no EcoFlow lines, add these two:

   ```python
   ECOFLOW_EMAIL    = "you@example.com"
   ECOFLOW_PASSWORD = "your EcoFlow password"
   ```

3. Restart the plugin with **Plugins → EcoFlow Cloud → Reload**, so it reads the file.

The plugin reads each line on its own, so you can put just one of them in the file and type the other into the **Configure** window. Whatever the file holds is used, whatever the **Configure** window says. Keep a copy of the file somewhere safe, such as a password manager, and never share it, as it holds your passwords.

## Each device's settings

Open these by double-clicking a power station in Indigo.

| Setting | What it does |
|---|---|
| **Serial Number** | The power station's serial number, as the EcoFlow app shows it under **Device Info**. When you change it, the plugin starts listening for the new one as soon as you click **Save**. |
| **Mirror Key States to Variables** | Tick this to have the main readings copied into Indigo variables in a folder called **EcoFlow**. It is unticked to start with. [Your devices](devices.md#readings-copied-to-variables) lists the readings and how the variables are named. |
