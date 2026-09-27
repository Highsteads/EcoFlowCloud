---
title: Getting started
nav_order: 2
---

# Getting started

This takes about five minutes, and you only do it once.

## What you need

- Indigo 2022.1 or later, on a Mac that can reach the internet.
- One or more EcoFlow **River 3** or **Delta 3** power stations, already set up in the EcoFlow app and connected to your Wi-Fi.
- The **email address and password** you use to sign in to the EcoFlow app.
- The **serial number** of each power station, which the EcoFlow app shows under **Device Info**.

## 1. Install the plugin

1. Go to the [Releases page](https://github.com/Highsteads/EcoFlowCloud/releases/latest) and download `EcoFlowCloud.indigoPlugin.zip`
2. Unzip the downloaded file — you will get `EcoFlowCloud.indigoPlugin`
3. Double-click `EcoFlowCloud.indigoPlugin` — Indigo will install it automatically

Indigo asks whether to enable the plugin. Say yes. The first time it starts, Indigo fetches the few add-on libraries the plugin needs, which takes a minute or so.

## 2. Sign in to EcoFlow

Open **Plugins → EcoFlow Cloud → Configure**.

1. Fill in **EcoFlow Email** and **EcoFlow Password** with your EcoFlow app sign-in.
2. Set **API Server** to the region your EcoFlow account belongs to: **EU / UK**, **US** or **Asia-Pacific**. EU / UK is chosen to start with.
3. Click **Save**.

If you would rather keep your EcoFlow sign-in in one shared file than in the plugin, the [Settings](settings.md) page shows how.

## 3. Add a power station

1. In Indigo, choose **New Device**.
2. Set **Type** to **EcoFlow Cloud**, then pick the model:
   - **EcoFlow River 3** for a River 3
   - **EcoFlow Delta 3** for a Delta 3
3. Type the power station's serial number into **Serial Number**, exactly as the EcoFlow app shows it.
4. Tick **Mirror Key States to Variables** only if you want the main readings copied into Indigo variables. The [Settings](settings.md) page explains what it does.
5. Click **Save**.

Add any other power stations the same way.

## 4. Connect

You do not need to do anything. As soon as you save a power station, the plugin starts listening for it and asks it for its readings. If this is your first power station, the plugin signs in to EcoFlow within about 10 seconds.

The same happens when you add another power station later or change a serial number.

## 5. Check it works

Within a few seconds the Event Log should say the plugin has logged in and connected, and then a line for each power station saying it is **online**. The device's **Device Online** state turns True and its readings fill in.

For a quick check of everything at once, choose **Plugins → EcoFlow Cloud → Log Device Status Summary**.

If nothing appears, the [When something goes wrong](troubleshooting.md) page goes through the usual causes.
