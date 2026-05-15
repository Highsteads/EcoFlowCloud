#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:    plugin.py
# Description: EcoFlow Cloud Indigo plugin — River 3 and Delta 3 integration
#              via EcoFlow private API + MQTT. Real-time monitoring and control.
# Author:      CliveS & Claude Sonnet 4.6
# Date:        15-05-2026
# Version:     1.2
#
# v1.2 (15-05-2026):
# - Fix race condition in _set_var() that caused intermittent
#   NameNotUniqueError warnings on every state mirror. Concurrent
#   _mirror_states calls (one per device) could both miss a new
#   variable in indigo.variables.iter() and both attempt to create
#   it. Switched to direct indigo.variables[name] lookup and wrapped
#   create() in try/except with a refresh-and-update fallback.
#
# v1.1 (11-05-2026):
# - CRITICAL FIX: corrected protobuf SetCommand field names — v1.0 had
#   AC output / DC output / AC charging power / max-charge / min-discharge
#   all mapped to fields that don't exist on the SetCommand message, so
#   those actions silently failed at the build step. Only XBoost worked.
# - Removed bogus class references in Delta3 decoder (Delta3CMSStatus and
#   Delta3BMSHeartbeatReport are not in the protobuf schema).
# - Generalised _extract_statistics to run for Delta3 as well as River3 so
#   cumulative energy counters come through on both devices.
# - Replaced os.getcwd()-based sys.path inserts with __file__-based
#   resolution — robust across thread contexts.
# - Removed unused threading.Lock.
# - Failed action sends now log at ERROR (was WARNING).
# - New states: firmware versions (pd/iot/mppt/inverter/bms), error codes
#   (errcode/bms/pd/mppt/inverter), fan_level, ac_out_freq_hz, sleep_state,
#   low_power_alarm, buzzer_on, screen_off_secs, ac_standby_secs,
#   dev_standby_secs, ac_out_energy_wh, ac_in_energy_wh, pv_in_energy_wh,
#   dc12v_out_energy_wh, typec_out_energy_wh, usba_out_energy_wh,
#   dev_work_seconds, typec2_w, dcp_w, dcp2_w, bms_w.
# - New actions: Set Buzzer, Set LCD Brightness, Set Screen Timeout,
#   Set Device Standby Timer.

import os
import sys
import time
from datetime import datetime

import indigo

# ---------------------------------------------------------------------------
# sys.path setup — must happen before any local imports.
# NOTE: __file__ is NOT defined for Indigo's main plugin.py (exec'd, not
# imported), so we use os.getcwd() which Indigo sets to Server Plugin/ at
# startup. Sub-modules like ecoflow_client.py have __file__ available and
# use that more robust path.
# ---------------------------------------------------------------------------

_here = os.getcwd()
if _here not in sys.path:
    sys.path.insert(0, _here)

# Bundle packages path
_pkg_path = os.path.abspath(os.path.join(_here, "..", "Packages"))
if os.path.isdir(_pkg_path) and _pkg_path not in sys.path:
    sys.path.insert(0, _pkg_path)

# Startup banner
try:
    from plugin_utils import log_startup_banner
except ImportError:
    log_startup_banner = None

# Secrets (optional — falls back to PluginConfig.xml)
sys.path.insert(0, "/Library/Application Support/Perceptive Automation")
try:
    from IndigoSecrets import ECOFLOW_EMAIL, ECOFLOW_PASSWORD
except ImportError:
    ECOFLOW_EMAIL    = ""
    ECOFLOW_PASSWORD = ""

from ecoflow_client import EcoFlowClient, apply_field_map

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLUGIN_ID      = "com.clives.indigoplugin.ecoflowcloud"
PLUGIN_NAME    = "EcoFlow Cloud"
# Plugin version is the source-of-truth one in Info.plist; this constant is
# only used in the startup banner fallback when log_startup_banner is missing.
PLUGIN_VERSION = "1.2"

VAR_FOLDER     = "EcoFlow"
DEVICE_TYPES   = {"ecoflowRiver3", "ecoflowDelta3"}
STALE_SECS     = 600    # 10 minutes without a message → mark offline
RECONNECT_SECS = 60     # seconds between reconnect attempts


# ---------------------------------------------------------------------------
# Plugin class
# ---------------------------------------------------------------------------

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        super().__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        # Credentials — prefer secrets.py, fall back to PluginConfig
        self.email    = ECOFLOW_EMAIL    or pluginPrefs.get("ecoflow_email", "").strip()
        self.password = ECOFLOW_PASSWORD or pluginPrefs.get("ecoflow_password", "").strip()

        # API server
        raw_server = pluginPrefs.get("api_server", "api-e.ecoflow.com")
        if raw_server == "custom":
            self.api_host = pluginPrefs.get("custom_api_host", "api-e.ecoflow.com").strip()
        else:
            self.api_host = raw_server

        # Logging level
        self.indigo_log_handler.setLevel(int(pluginPrefs.get("logLevel", 20)))

        # State tracking
        self.client           = None
        self.last_seen        = {}   # {dev_id: float}  unix timestamp
        self._reconnect_at    = 0    # unix timestamp when next reconnect allowed
        self._var_folder_id   = None

        # Startup banner
        creds_ok = "Yes" if (self.email and self.password) else "No (check config)"
        if log_startup_banner:
            log_startup_banner(pluginId, pluginDisplayName, pluginVersion, extras=[
                ("API Server:",    self.api_host),
                ("Credentials:",   creds_ok),
            ])
        else:
            indigo.server.log(f"{pluginDisplayName} v{pluginVersion} starting")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def startup(self):
        self.logger.info(f"{PLUGIN_NAME} starting up")
        self._connect_mqtt()

    def shutdown(self):
        self.logger.info(f"{PLUGIN_NAME} shutting down")
        if self.client:
            self.client.disconnect()
            self.client = None

    def deviceStartComm(self, dev):
        self.logger.debug(f"deviceStartComm: {dev.name} ({dev.deviceTypeId})")
        dev.stateListOrDisplayStateIdChanged()
        self.last_seen[dev.id] = time.time()
        dev.updateStateOnServer("deviceOnline", False)
        dev.updateStateOnServer("lastUpdate", "")

    def deviceStopComm(self, dev):
        self.logger.debug(f"deviceStopComm: {dev.name}")
        self.last_seen.pop(dev.id, None)

    def deviceUpdated(self, origDev, newDev):
        # Required for subscribeToChanges — not used here, but must be defined
        pass

    # ------------------------------------------------------------------
    # Plugin preferences updated
    # ------------------------------------------------------------------

    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        if not userCancelled:
            new_email = ECOFLOW_EMAIL or valuesDict.get("ecoflow_email", "").strip()
            new_pass  = ECOFLOW_PASSWORD or valuesDict.get("ecoflow_password", "").strip()
            raw_srv   = valuesDict.get("api_server", "api-e.ecoflow.com")
            new_host  = valuesDict.get("custom_api_host", "api-e.ecoflow.com").strip() \
                        if raw_srv == "custom" else raw_srv

            self.indigo_log_handler.setLevel(int(valuesDict.get("logLevel", 20)))

            creds_changed = (new_email != self.email or
                             new_pass  != self.password or
                             new_host  != self.api_host)
            self.email    = new_email
            self.password = new_pass
            self.api_host = new_host

            if creds_changed:
                self.logger.info("Credentials or server changed — reconnecting")
                self._reconnect_at = 0
                if self.client:
                    self.client.disconnect()
                    self.client = None
                self._connect_mqtt()

    def getPrefsConfigUiValues(self):
        values = self.pluginPrefs
        errors = indigo.Dict()
        # Pre-populate from secrets.py if pref is blank
        if not values.get("ecoflow_email") and ECOFLOW_EMAIL:
            values["ecoflow_email"] = ECOFLOW_EMAIL
        if not values.get("ecoflow_password") and ECOFLOW_PASSWORD:
            values["ecoflow_password"] = ECOFLOW_PASSWORD
        return values, errors

    def validatePrefsConfigUi(self, valuesDict):
        errors = indigo.Dict()
        email    = ECOFLOW_EMAIL    or valuesDict.get("ecoflow_email", "").strip()
        password = ECOFLOW_PASSWORD or valuesDict.get("ecoflow_password", "").strip()
        if not email:
            errors["ecoflow_email"] = "EcoFlow email is required (or set ECOFLOW_EMAIL in secrets.py)"
        if not password:
            errors["ecoflow_password"] = "EcoFlow password is required (or set ECOFLOW_PASSWORD in secrets.py)"
        if errors:
            return False, valuesDict, errors
        return True, valuesDict

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def runConcurrentThread(self):
        try:
            while True:
                self.sleep(10)
                now = time.time()

                # Reconnect if disconnected and backoff elapsed
                if self.client is None or not self.client.connected:
                    if now >= self._reconnect_at:
                        self.logger.info("[EcoFlow] MQTT not connected — attempting reconnect")
                        self._connect_mqtt()
                        self._reconnect_at = now + RECONNECT_SECS

                # Stale detection
                for dev in indigo.devices.iter("self"):
                    if not dev.enabled or not dev.configured:
                        continue
                    last = self.last_seen.get(dev.id, now)
                    if (now - last) > STALE_SECS:
                        if dev.states.get("deviceOnline", False):
                            dev.updateStateOnServer("deviceOnline", False)
                            self.logger.warning(f'[{dev.name}] offline - no message for >{STALE_SECS}s')

        except self.StopThread:
            pass

    # ------------------------------------------------------------------
    # MQTT connection management
    # ------------------------------------------------------------------

    def _connect_mqtt(self):
        """Authenticate and connect MQTT. Safe to call multiple times."""
        if not self.email or not self.password:
            self.logger.warning("[EcoFlow] No credentials configured — cannot connect")
            return

        # Build serial → device_type map from configured Indigo devices
        serial_to_type = {}
        for dev in indigo.devices.iter("self"):
            if not dev.enabled or not dev.configured:
                continue
            serial = dev.pluginProps.get("serial_number", "").strip()
            if serial:
                serial_to_type[serial] = dev.deviceTypeId

        if not serial_to_type:
            self.logger.info("[EcoFlow] No configured devices — MQTT not started")
            return

        # Create client
        self.client = EcoFlowClient(
            api_host       = self.api_host,
            email          = self.email,
            password       = self.password,
            on_message_cb  = self._on_ecoflow_message,
            on_connect_cb  = self._on_mqtt_connect,
            logger         = self.logger,
        )

        if not self.client.authenticate():
            self.logger.error("[EcoFlow] Authentication failed — will retry")
            self.client = None
            return

        if not self.client.connect(serial_to_type):
            self.logger.error("[EcoFlow] MQTT connect failed — will retry")
            self.client = None

    def _on_mqtt_connect(self, connected):
        """Called by paho-mqtt thread when connection state changes."""
        if connected:
            self.logger.info("[EcoFlow] MQTT ready — waiting for device data")
        else:
            self.logger.warning("[EcoFlow] MQTT connection lost")

    # ------------------------------------------------------------------
    # Message handler
    # ------------------------------------------------------------------

    def _on_ecoflow_message(self, serial, flat_dict):
        """Called by EcoFlowClient on each decoded MQTT message."""
        dev = self._find_device_by_serial(serial)
        if not dev:
            self.logger.debug(f"[EcoFlow] No Indigo device for serial {serial}")
            return

        kv, mirror = apply_field_map(flat_dict, dev.deviceTypeId)
        if not kv:
            return

        now_str = datetime.now().strftime("%H:%M:%S")
        kv.append({"key": "lastUpdate", "value": now_str, "uiValue": now_str})

        # Mark online
        was_offline = not dev.states.get("deviceOnline", False)
        kv.append({"key": "deviceOnline", "value": True, "uiValue": "true"})

        try:
            dev.updateStatesOnServer(kv)
        except Exception as exc:
            self.logger.warning(f'[{dev.name}] updateStates error: {exc}')
            return

        self.last_seen[dev.id] = time.time()

        if was_offline:
            self.logger.info(f'[{dev.name}] online - first message received')

        # Variable mirroring
        if dev.pluginProps.get("mirror_to_variable", False) and mirror:
            self._mirror_states(dev, mirror)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def actionSetACOutput(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        state = action.props.get("ac_state", "on")
        self._send_action(dev, "ac_out_en", 1 if state == "on" else 0, f"AC output -> {state}")

    def actionSetDCOutput(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        state = action.props.get("dc_state", "on")
        self._send_action(dev, "dc_en", 1 if state == "on" else 0, f"DC output -> {state}")

    def actionSetXBoost(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        state = action.props.get("xboost_state", "on")
        self._send_action(dev, "xboost_en", 1 if state == "on" else 0, f"XBoost -> {state}")

    def actionSetMaxChargeSoc(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        soc = int(action.props.get("max_soc", 100))
        self._send_action(dev, "max_charge_soc", soc, f"Max charge -> {soc}%")

    def actionSetMinDischargeSoc(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        soc = int(action.props.get("min_soc", 0))
        self._send_action(dev, "min_discharge_soc", soc, f"Min discharge -> {soc}%")

    def actionSetACChargingPower(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        watts = int(action.props.get("charge_watts", 305))
        self._send_action(dev, "ac_charging_w", watts, f"AC charge rate -> {watts} W")

    def actionSetBuzzer(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        state = action.props.get("buzzer_state", "on")
        self._send_action(dev, "buzzer_on", 1 if state == "on" else 0,
                          f"Buzzer -> {state}")

    def actionSetLCDBrightness(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        level = max(0, min(100, int(action.props.get("brightness", 50))))
        self._send_action(dev, "lcd_brightness", level,
                          f"LCD brightness -> {level}")

    def actionSetScreenTimeout(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        secs = max(0, int(action.props.get("screen_secs", 300)))
        self._send_action(dev, "screen_off_secs", secs,
                          f"Screen timeout -> {secs}s")

    def actionSetDeviceStandby(self, action, dev=None, callerWaitingForResult=None):
        dev = indigo.devices[action.deviceId]
        secs = max(0, int(action.props.get("standby_secs", 0)))
        self._send_action(dev, "dev_standby_secs", secs,
                          f"Device standby -> {secs}s (0 = never)")

    def _send_action(self, dev, action_key, value, log_label):
        """Common action sender with validation."""
        if not dev.states.get("deviceOnline", False):
            self.logger.warning(f'[{dev.name}] action skipped: device offline')
            return
        if not self.client or not self.client.connected:
            self.logger.warning(f'[{dev.name}] action skipped: MQTT not connected')
            return
        serial = dev.pluginProps.get("serial_number", "").strip()
        if not serial:
            self.logger.error(f'[{dev.name}] action skipped: no serial number configured')
            return
        ok = self.client.send_command(serial, dev.deviceTypeId, action_key, value)
        if ok:
            self.logger.info(f'[{dev.name}] {log_label}')
        else:
            self.logger.error(f'[{dev.name}] command send FAILED: {log_label}')

    # ------------------------------------------------------------------
    # Menu callbacks
    # ------------------------------------------------------------------

    def menuRefreshConnection(self, valuesDict=None, typeId=None):
        self.logger.info("Reconnect requested via menu")
        if self.client:
            self.client.disconnect()
            self.client = None
        self._reconnect_at = 0
        self._connect_mqtt()
        return True

    def menuDeviceStatus(self, valuesDict=None, typeId=None):
        now = time.time()
        count = 0
        for dev in indigo.devices.iter("self"):
            count += 1
            serial  = dev.pluginProps.get("serial_number", "(none)")
            online  = dev.states.get("deviceOnline", False)
            soc     = dev.states.get("battery_soc", "--")
            pwr_in  = dev.states.get("power_in_w",  "--")
            pwr_out = dev.states.get("power_out_w", "--")
            last    = dev.states.get("lastUpdate", "--")
            age     = int(now - self.last_seen.get(dev.id, now))
            status  = "ONLINE" if online else "OFFLINE"
            indigo.server.log(
                f"  [{status}] {dev.name} ({dev.deviceTypeId}) SN={serial} | "
                f"SOC={soc}% | In={pwr_in}W Out={pwr_out}W | last={last} ({age}s ago)"
            )
        if count == 0:
            indigo.server.log("  (no EcoFlow devices configured)")
        mqtt_state = "connected" if (self.client and self.client.connected) else "disconnected"
        indigo.server.log(f"  MQTT: {mqtt_state} | API: {self.api_host}")
        return True

    def showPluginInfo(self, valuesDict=None, typeId=None):
        creds_ok = "Yes" if (self.email and self.password) else "No (check config)"
        if log_startup_banner:
            log_startup_banner(self.pluginId, self.pluginDisplayName, self.pluginVersion, extras=[
                ("API Server:",  self.api_host),
                ("Credentials:", creds_ok),
            ])
        else:
            indigo.server.log(f"{self.pluginDisplayName} v{self.pluginVersion}")

    # ------------------------------------------------------------------
    # Variable mirroring
    # ------------------------------------------------------------------

    def _mirror_states(self, dev, mirror):
        """Write selected states to Indigo variables in the EcoFlow folder."""
        try:
            folder_id = self._get_or_create_var_folder()
            prefix    = "ecoflow_" + _sanitise_var_name(dev.name)[:28]
            for suffix, value in mirror.items():
                var_name = f"{prefix}_{suffix}"
                self._set_var(var_name, folder_id, str(value))
        except Exception as exc:
            self.logger.warning(f'[{dev.name}] variable mirror error: {exc}')

    def _get_or_create_var_folder(self):
        if self._var_folder_id is not None:
            return self._var_folder_id
        for folder in indigo.variables.folders:
            if folder.name == VAR_FOLDER:
                self._var_folder_id = folder.id
                return folder.id
        folder = indigo.variables.folder.create(VAR_FOLDER)
        self._var_folder_id = folder.id
        return folder.id

    def _set_var(self, name, folder_id, value):
        # Direct lookup — variable names are globally unique in Indigo.
        try:
            var = indigo.variables[name]
            if var.value != value:
                indigo.variable.updateValue(var.id, value)
            return
        except (KeyError, ValueError):
            pass
        # Create — wrap in try/except for race safety. Multiple devices
        # can mirror concurrently; without a lock, two callers can both
        # miss the lookup and both try to create the same new variable.
        try:
            indigo.variable.create(name, value=value, folder=folder_id)
        except Exception as exc:
            try:
                var = indigo.variables[name]
                if var.value != value:
                    indigo.variable.updateValue(var.id, value)
            except Exception:
                self.logger.warning(f'_set_var: cannot set {name} = {value}: {exc}')

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_device_by_serial(self, serial):
        for dev in indigo.devices.iter("self"):
            if dev.pluginProps.get("serial_number", "").strip() == serial:
                return dev
        return None


# ---------------------------------------------------------------------------
# Module helpers
# ---------------------------------------------------------------------------

def _sanitise_var_name(name):
    """Replace non-alphanumeric characters with underscores for variable names."""
    out = []
    for c in name:
        out.append(c if c.isalnum() else "_")
    return "".join(out)
