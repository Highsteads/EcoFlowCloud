#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:    ecoflow_client.py
# Description: EcoFlow cloud authentication and MQTT client for Indigo plugin
# Author:      CliveS & Claude Sonnet 4.6
# Date:        11-05-2026
# Version:     1.1

import base64
import json
import os
import random
import ssl
import sys
import time

import requests

# Packages bundled in Contents/Packages/
_pkg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Packages")
if os.path.isdir(_pkg_path) and _pkg_path not in sys.path:
    sys.path.insert(0, _pkg_path)

import paho.mqtt.client as mqtt

# Protobuf modules live in the same folder as this file. Use __file__-based
# discovery rather than os.getcwd() — cwd is not guaranteed to be Server Plugin/
# in every invocation (set commands run on the MQTT thread).
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

try:
    import ef_river3_pb2
    import ef_delta3_pb2
    from google.protobuf.json_format import MessageToDict
    _PROTO_OK = True
except ImportError as e:
    _PROTO_OK = False
    _PROTO_ERR = str(e)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MQTT_BROKER   = "mqtt.ecoflow.com"
MQTT_PORT     = 8883
MQTT_KEEPALIVE = 60
API_TIMEOUT   = 15       # seconds for REST calls
RECONNECT_DELAY = 30     # seconds between reconnect attempts

# bms_chg_dsg_state integer values
CHG_STATE_IDLE        = 0
CHG_STATE_DISCHARGING = 1
CHG_STATE_CHARGING    = 2
CHG_STATE_LABELS = {
    CHG_STATE_IDLE:        "idle",
    CHG_STATE_DISCHARGING: "discharging",
    CHG_STATE_CHARGING:    "charging",
}

# River3 BMS heartbeat command pairs
RIVER3_BMS_HEARTBEAT = {
    (3, 50), (3, 51), (3, 52),
}

# Delta3 BMS heartbeat command pairs
DELTA3_BMS_HEARTBEAT = {
    (3, 50), (3, 51), (3, 52),
}

# ---------------------------------------------------------------------------
# Field maps: protobuf field name -> (indigo_state_id, python_type, ui_fmt)
# ui_fmt: format string using {v}, or None for raw bool
# ---------------------------------------------------------------------------

COMMON_FIELD_MAP = {
    # Battery
    "bms_batt_soc":         ("battery_soc",       int,   "{v}%"),
    "bms_batt_soh":         ("battery_soh",        int,   "{v}%"),
    "bms_remain_cap":       ("battery_remain_wh",  int,   "{v} Wh"),
    "bms_full_cap":         ("battery_full_cap_wh",int,   "{v} Wh"),
    "bms_design_cap":       ("battery_design_wh",  int,   "{v} Wh"),
    "bms_batt_vol":         ("battery_voltage",    float, "{v:.2f} V"),
    "bms_min_cell_temp":    ("cell_temp_min_c",    float, "{v:.1f} C"),
    "bms_max_cell_temp":    ("cell_temp_max_c",    float, "{v:.1f} C"),
    "cycles":               ("cycles",             int,   "{v}"),
    "bms_chg_dsg_state":    ("charging_state",     None,  None),  # special: enum
    "cms_chg_dsg_state":    ("charging_state",     None,  None),  # Delta3 alt
    # Power
    "pow_in_sum_w":         ("power_in_w",         int,   "{v} W"),
    "pow_out_sum_w":        ("power_out_w",        int,   "{v} W"),
    "pow_get_pv":           ("solar_in_w",         int,   "{v} W"),
    "pow_get_ac_in":        ("ac_in_w",            int,   "{v} W"),
    "pow_get_ac_out":       ("ac_out_w",           int,   "{v} W"),
    "pow_get_12v":          ("dc_12v_w",           int,   "{v} W"),
    "pow_get_typec1":       ("typec1_w",           int,   "{v} W"),
    "pow_get_typec2":       ("typec2_w",           int,   "{v} W"),
    "pow_get_qcusb1":       ("usb1_w",             int,   "{v} W"),
    "pow_get_qcusb2":       ("usb2_w",             int,   "{v} W"),
    "pow_get_dcp":          ("dcp_w",              int,   "{v} W"),
    "pow_get_dcp2":         ("dcp2_w",             int,   "{v} W"),
    "pow_get_bms":          ("bms_w",              int,   "{v} W"),
    # Time estimates — prefer cms_* over bms_* on Delta3 (last write wins;
    # cms_* keys are listed after bms_* so they overwrite when both arrive)
    "bms_chg_rem_time":     ("charge_mins",        int,   "{v} min"),
    "bms_dsg_rem_time":     ("discharge_mins",     int,   "{v} min"),
    "cms_chg_rem_time":     ("charge_mins",        int,   "{v} min"),
    "cms_dsg_rem_time":     ("discharge_mins",     int,   "{v} min"),
    # Temperatures
    "temp_pcs_dc":          ("temp_dc_c",          float, "{v:.1f} C"),
    "temp_pcs_ac":          ("temp_ac_c",          float, "{v:.1f} C"),
    "pcs_fan_level":        ("fan_level",          int,   "{v}"),
    # Control states (incoming telemetry)
    "ac_out_en":            ("ac_out_en",          bool,  None),
    "cfg_ac_out_open":      ("ac_out_en",          bool,  None),  # Delta3 telemetry alt
    "dc_12v_en":            ("dc_en",              bool,  None),
    "dc_en":                ("dc_en",              bool,  None),
    "dc_out_open":          ("dc_en",              bool,  None),  # alt telemetry name
    "xboost_en":            ("xboost_en",          bool,  None),
    "bms_max_chg_soc":      ("max_charge_soc",     int,   "{v}%"),
    "bms_min_dsg_soc":      ("min_discharge_soc",  int,   "{v}%"),
    "cms_max_chg_soc":      ("max_charge_soc",     int,   "{v}%"),
    "cms_min_dsg_soc":      ("min_discharge_soc",  int,   "{v}%"),
    "ac_charging_power":    ("ac_charging_w",      int,   "{v} W"),
    "plug_in_info_ac_in_chg_pow_max": ("ac_charging_w", int, "{v} W"),
    # Settings telemetry
    "en_beep":              ("buzzer_on",          bool,  None),
    "screen_off_time":      ("screen_off_secs",    int,   "{v} s"),
    "ac_standby_time":      ("ac_standby_secs",    int,   "{v} s"),
    "dev_standby_time":     ("dev_standby_secs",   int,   "{v} s"),
    # Diagnostics
    "errcode":              ("error_code",         int,   "{v}"),
    "bms_err_code":         ("bms_error_code",     int,   "{v}"),
    "pd_err_code":          ("pd_error_code",      int,   "{v}"),
    "mppt_err_code":        ("mppt_error_code",    int,   "{v}"),
    "llc_inv_err_code":     ("inverter_error_code", int,  "{v}"),
    "low_power_alarm":      ("low_power_alarm",    bool,  None),
    "dev_sleep_state":      ("sleep_state",        int,   "{v}"),
    "ac_out_freq":          ("ac_out_freq_hz",     int,   "{v} Hz"),
    # Firmware versions (RuntimePropertyUpload)
    "pd_firm_ver":          ("pd_firmware",        int,   "{v}"),
    "iot_firm_ver":         ("iot_firmware",       int,   "{v}"),
    "mppt_firm_ver":        ("mppt_firmware",      int,   "{v}"),
    "llc_inv_firm_ver":     ("inverter_firmware",  int,   "{v}"),
    "bms_firm_ver":         ("bms_firmware",       int,   "{v}"),
    # Cumulative energy counters (populated by _extract_statistics —
    # enum names from ef_*_pb2.*StatisticsObject, prefix stripped + lowercased)
    "ac_out_energy":        ("ac_out_energy_wh",     int, "{v} Wh"),
    "ac_in_energy":         ("ac_in_energy_wh",      int, "{v} Wh"),
    "pv_in_energy":         ("pv_in_energy_wh",      int, "{v} Wh"),
    "dc12v_out_energy":     ("dc12v_out_energy_wh",  int, "{v} Wh"),
    "typec_out_energy":     ("typec_out_energy_wh",  int, "{v} Wh"),
    "usba_out_energy":      ("usba_out_energy_wh",   int, "{v} Wh"),
    "dev_work_time":        ("dev_work_seconds",     int, "{v} s"),
}

DELTA3_EXTRA_FIELD_MAP = {
    "plug_in_info_ac_out_vol": ("ac_out_voltage", int, "{v} V"),
}

# Merged map for Delta3
DELTA3_FIELD_MAP = {**COMMON_FIELD_MAP, **DELTA3_EXTRA_FIELD_MAP}

# Command field names per device type — the SetCommand protobuf field name
# that an action_key maps to. Verified against ef_*_pb2.*SetCommand
# descriptors on 11-05-2026 (v1.0 had the AC/DC/AC-charge mappings wrong:
# ac_out_en / dc_en / ac_charging_power do not exist on SetCommand).
_COMMON_CMD_FIELDS = {
    "ac_out_en":          "cfg_ac_out_open",
    "dc_en":              "cfg_dc12v_out_open",
    "xboost_en":          "xboost_en",
    "ac_charging_w":      "plug_in_info_ac_in_chg_pow_max",
    "buzzer_on":          "en_beep",
    "lcd_brightness":     "lcd_light",
    "screen_off_secs":    "screen_off_time",
    "dev_standby_secs":   "dev_standby_time",
    "ac_standby_secs":    "ac_standby_time",
    "dc_standby_secs":    "dc_standby_time",
}

CMD_FIELDS = {
    "ecoflowRiver3": {
        **_COMMON_CMD_FIELDS,
        "max_charge_soc":     "cms_max_chg_soc",
        "min_discharge_soc":  "cms_min_dsg_soc",
    },
    "ecoflowDelta3": {
        **_COMMON_CMD_FIELDS,
        "max_charge_soc":     "cms_max_chg_soc",
        "min_discharge_soc":  "cms_min_dsg_soc",
    },
}


# ---------------------------------------------------------------------------
# EcoFlowClient
# ---------------------------------------------------------------------------

class EcoFlowClient:
    """
    Handles EcoFlow Private API authentication and MQTT connectivity for
    one or more devices. Calls on_message_cb(serial, field_dict) for each
    incoming MQTT update. Calls on_connect_cb(connected: bool) on state changes.
    """

    def __init__(self, api_host, email, password, on_message_cb, on_connect_cb, logger):
        self.api_host       = api_host
        self.email          = email
        self.password       = password
        self.on_message_cb  = on_message_cb
        self.on_connect_cb  = on_connect_cb
        self.logger         = logger

        self.token           = None
        self.user_id         = None
        self.mqtt_username   = None
        self.mqtt_password   = None
        self.mqtt_client_id  = None

        self._mqtt           = None
        self.connected       = False
        self._serial_to_type = {}   # {serial: device_type_id}

        if not _PROTO_OK:
            self.logger.error(f"[EcoFlow] Protobuf import failed: {_PROTO_ERR}")
            self.logger.error("[EcoFlow] Ensure paho-mqtt and protobuf are installed in Contents/Packages/")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def authenticate(self):
        """Perform REST login + MQTT credential exchange. Returns True on success."""
        try:
            self.logger.info(f"[EcoFlow] Authenticating with {self.api_host} ...")
            url     = f"https://{self.api_host}/auth/login"
            headers = {"lang": "en_US", "content-type": "application/json"}
            payload = {
                "email":    self.email,
                "password": base64.b64encode(self.password.encode()).decode(),
                "scene":    "IOT_APP",
                "userType": "ECOFLOW",
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if data.get("message", "").lower() != "success":
                self.logger.error(f"[EcoFlow] Login failed: {data.get('message')}")
                return False

            self.token   = data["data"]["token"]
            self.user_id = data["data"]["user"]["userId"]
            user_name    = data["data"]["user"].get("name", "unknown")
            self.logger.info(f"[EcoFlow] Logged in as: {user_name} (userId={self.user_id})")

        except requests.exceptions.RequestException as exc:
            self.logger.error(f"[EcoFlow] Login request failed: {exc}")
            return False
        except (KeyError, ValueError) as exc:
            self.logger.error(f"[EcoFlow] Login response parse error: {exc}")
            return False

        # Fetch MQTT credentials
        try:
            cert_url     = f"https://{self.api_host}/iot-auth/app/certification"
            cert_headers = {
                "lang":          "en_US",
                "Authorization": f"Bearer {self.token}",
            }
            resp = requests.get(cert_url, headers=cert_headers,
                                params={"userId": self.user_id}, timeout=API_TIMEOUT)
            resp.raise_for_status()
            cdata = resp.json()

            if cdata.get("message", "").lower() != "success":
                self.logger.error(f"[EcoFlow] MQTT certification failed: {cdata.get('message')}")
                return False

            self.mqtt_username  = cdata["data"]["certificateAccount"]
            self.mqtt_password  = cdata["data"]["certificatePassword"]
            self.logger.info(f"[EcoFlow] MQTT credentials obtained for account: {self.mqtt_username}")

        except requests.exceptions.RequestException as exc:
            self.logger.error(f"[EcoFlow] MQTT certification request failed: {exc}")
            return False
        except (KeyError, ValueError) as exc:
            self.logger.error(f"[EcoFlow] MQTT certification parse error: {exc}")
            return False

        # Generate stable client ID (same format as mobile app)
        self.mqtt_client_id = self._gen_client_id()
        return True

    def connect(self, serial_to_type):
        """
        Connect to MQTT broker and subscribe to all device topics.
        serial_to_type: dict {serial_number: device_type_id}
        Returns True if connection initiated (does not wait for CONNACK).
        """
        if not self.token or not self.mqtt_username:
            self.logger.error("[EcoFlow] Cannot connect: not authenticated")
            return False

        self._serial_to_type = dict(serial_to_type)

        try:
            # paho-mqtt 2.x requires explicit CallbackAPIVersion
            try:
                self._mqtt = mqtt.Client(
                    callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
                    client_id=self.mqtt_client_id,
                    protocol=mqtt.MQTTv311,
                )
            except AttributeError:
                # paho-mqtt 1.x — no CallbackAPIVersion
                self._mqtt = mqtt.Client(
                    client_id=self.mqtt_client_id,
                    protocol=mqtt.MQTTv311,
                )

            self._mqtt.username_pw_set(self.mqtt_username, self.mqtt_password)

            # Disable paho auto-reconnect — our runConcurrentThread manages this
            self._mqtt.reconnect_delay_set(min_delay=120, max_delay=120)

            # TLS
            tls_ctx = ssl.create_default_context()
            tls_ctx.check_hostname = True
            tls_ctx.verify_mode    = ssl.CERT_REQUIRED
            self._mqtt.tls_set_context(tls_ctx)

            # Callbacks
            self._mqtt.on_connect    = self._on_connect
            self._mqtt.on_disconnect = self._on_disconnect
            self._mqtt.on_message    = self._on_message

            self.logger.info(f"[EcoFlow] Connecting to {MQTT_BROKER}:{MQTT_PORT} ...")
            self._mqtt.connect(MQTT_BROKER, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
            self._mqtt.loop_start()
            return True

        except Exception as exc:
            self.logger.error(f"[EcoFlow] MQTT connect error: {exc}")
            return False

    def disconnect(self):
        """Stop MQTT loop and disconnect cleanly."""
        self.connected = False
        if self._mqtt:
            try:
                self._mqtt.loop_stop()
                self._mqtt.disconnect()
            except Exception:
                pass
            self._mqtt = None
        self.logger.info("[EcoFlow] MQTT disconnected")

    def send_command(self, serial, device_type_id, action_key, value):
        """
        Send a protobuf command to the device via MQTT.
        action_key: logical name (e.g. "ac_out_en", "max_charge_soc")
        value:      integer value to set
        Returns True on success.
        """
        if not _PROTO_OK:
            self.logger.error("[EcoFlow] Cannot send command: protobuf not available")
            return False
        if not self.connected:
            self.logger.warning(f"[EcoFlow] Cannot send command to {serial}: not connected")
            return False

        # Resolve protobuf field name
        field_map = CMD_FIELDS.get(device_type_id, {})
        proto_field = field_map.get(action_key)
        if not proto_field:
            self.logger.error(f"[EcoFlow] Unknown action key '{action_key}' for {device_type_id}")
            return False

        try:
            if device_type_id == "ecoflowRiver3":
                raw = self._build_river3_command(proto_field, int(value), serial)
            elif device_type_id == "ecoflowDelta3":
                raw = self._build_delta3_command(proto_field, int(value), serial)
            else:
                self.logger.error(f"[EcoFlow] Unknown device type: {device_type_id}")
                return False

            if raw is None:
                return False

            topic = f"/app/{self.user_id}/{serial}/thing/property/set"
            result = self._mqtt.publish(topic, raw, qos=1)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.warning(f"[EcoFlow] Publish failed (rc={result.rc})")
                return False

            self.logger.debug(f"[EcoFlow] Command sent to {serial}: {action_key}={value}")
            return True

        except Exception as exc:
            self.logger.error(f"[EcoFlow] Command build/send error: {exc}")
            return False

    # ------------------------------------------------------------------
    # MQTT callbacks
    # ------------------------------------------------------------------

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.logger.info("[EcoFlow] MQTT connected successfully")

            # Subscribe to all device data topics
            for serial in self._serial_to_type:
                topic = f"/app/device/property/{serial}"
                client.subscribe(topic, qos=1)
                self.logger.info(f"[EcoFlow] Subscribed to {topic}")

            self.on_connect_cb(True)
        else:
            self.connected = False
            self.logger.error(f"[EcoFlow] MQTT connection refused (rc={rc}): {_mqtt_rc_desc(rc)}")
            self.on_connect_cb(False)

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc == 0:
            self.logger.info("[EcoFlow] MQTT disconnected cleanly")
        else:
            self.logger.warning(f"[EcoFlow] MQTT disconnected unexpectedly (rc={rc})")
        self.on_connect_cb(False)

    def _on_message(self, client, userdata, msg):
        try:
            # Extract serial from topic: /app/device/property/{serial}
            parts = msg.topic.split("/")
            if len(parts) < 4:
                return
            serial = parts[-1]

            device_type_id = self._serial_to_type.get(serial)
            if not device_type_id:
                self.logger.debug(f"[EcoFlow] Message from unknown serial: {serial}")
                return

            if not _PROTO_OK:
                return

            raw = msg.payload

            if device_type_id == "ecoflowRiver3":
                field_dict = self._decode_river3_message(raw)
            elif device_type_id == "ecoflowDelta3":
                field_dict = self._decode_delta3_message(raw)
            else:
                return

            if field_dict:
                self.on_message_cb(serial, field_dict)

        except Exception as exc:
            self.logger.debug(f"[EcoFlow] Message handler error: {exc}")

    # ------------------------------------------------------------------
    # River3 message decoding
    # ------------------------------------------------------------------

    def _decode_river3_message(self, raw):
        """Decode a raw MQTT payload for River 3. Returns flat field dict."""
        import base64 as _b64
        try:
            try:
                raw = _b64.b64decode(raw, validate=True)
            except Exception:
                pass  # not base64 — use as-is

            header_msg = ef_river3_pb2.River3HeaderMessage()
            header_msg.ParseFromString(raw)

            if not header_msg.header:
                return {}

            header   = header_msg.header[0]
            pdata    = getattr(header, "pdata", b"")
            if not pdata:
                return {}

            enc_type = getattr(header, "enc_type", 0)
            src      = getattr(header, "src", 0)
            seq      = getattr(header, "seq", 0)
            cmd_func = getattr(header, "cmd_func", 0)
            cmd_id   = getattr(header, "cmd_id", 0)

            if enc_type == 1 and src != 32:
                pdata = _xor_decode(pdata, seq)

            decoded = self._decode_river3_pdata(pdata, cmd_func, cmd_id)
            return _flatten_dict(decoded) if decoded else {}

        except Exception as exc:
            self.logger.debug(f"[EcoFlow] River3 decode error: {exc}")
            return {}

    def _decode_river3_pdata(self, pdata, cmd_func, cmd_id):
        try:
            if cmd_func == 254 and cmd_id == 21:
                msg = ef_river3_pb2.River3DisplayPropertyUpload()
                msg.ParseFromString(pdata)
                result = MessageToDict(msg, preserving_proto_field_name=True)
                return _extract_statistics(result, ef_river3_pb2,
                                          "River3StatisticsObject")
            elif cmd_func == 254 and cmd_id == 22:
                msg = ef_river3_pb2.River3RuntimePropertyUpload()
                msg.ParseFromString(pdata)
                return MessageToDict(msg, preserving_proto_field_name=True)
            elif cmd_func == 32 and cmd_id == 2:
                msg = ef_river3_pb2.River3CMSHeartBeatReport()
                msg.ParseFromString(pdata)
                return MessageToDict(msg, preserving_proto_field_name=True)
            elif (cmd_func, cmd_id) in RIVER3_BMS_HEARTBEAT or cmd_func not in (254,):
                msg = ef_river3_pb2.River3BMSHeartBeatReport()
                msg.ParseFromString(pdata)
                return MessageToDict(msg, preserving_proto_field_name=True)
        except Exception as exc:
            self.logger.debug(f"[EcoFlow] River3 pdata decode ({cmd_func},{cmd_id}): {exc}")
        return {}

    # ------------------------------------------------------------------
    # Delta3 message decoding
    # ------------------------------------------------------------------

    def _decode_delta3_message(self, raw):
        """Decode a raw MQTT payload for Delta 3. Returns flat field dict."""
        import base64 as _b64
        try:
            try:
                raw = _b64.b64decode(raw, validate=True)
            except Exception:
                pass

            header_msg = ef_delta3_pb2.Delta3HeaderMessage()
            header_msg.ParseFromString(raw)

            if not header_msg.header:
                return {}

            header   = header_msg.header[0]
            pdata    = getattr(header, "pdata", b"")
            if not pdata:
                return {}

            enc_type = getattr(header, "enc_type", 0)
            src      = getattr(header, "src", 0)
            seq      = getattr(header, "seq", 0)
            cmd_func = getattr(header, "cmd_func", 0)
            cmd_id   = getattr(header, "cmd_id", 0)

            if enc_type == 1 and src != 32:
                pdata = _xor_decode(pdata, seq)

            decoded = self._decode_delta3_pdata(pdata, cmd_func, cmd_id)
            return _flatten_dict(decoded) if decoded else {}

        except Exception as exc:
            self.logger.debug(f"[EcoFlow] Delta3 decode error: {exc}")
            return {}

    def _decode_delta3_pdata(self, pdata, cmd_func, cmd_id):
        # Delta3 protobuf only exposes Display/Runtime upload classes —
        # Delta3CMSStatus and Delta3BMSHeartbeatReport are not in the schema
        # despite v1.0 referencing them (which silently fell through to {}).
        try:
            if cmd_func == 254 and cmd_id == 21:
                msg = ef_delta3_pb2.Delta3DisplayPropertyUpload()
                msg.ParseFromString(pdata)
                result = MessageToDict(msg, preserving_proto_field_name=True)
                return _extract_statistics(result, ef_delta3_pb2,
                                          "Delta3StatisticsObject")
            elif cmd_func == 254 and cmd_id == 22:
                msg = ef_delta3_pb2.Delta3RuntimePropertyUpload()
                msg.ParseFromString(pdata)
                return MessageToDict(msg, preserving_proto_field_name=True)
        except Exception as exc:
            self.logger.debug(f"[EcoFlow] Delta3 pdata decode ({cmd_func},{cmd_id}): {exc}")
        return {}

    # ------------------------------------------------------------------
    # Command builders
    # ------------------------------------------------------------------

    def _build_river3_command(self, proto_field, value, serial):
        """Build and return raw protobuf bytes for a River3 set command."""
        try:
            payload = ef_river3_pb2.River3SetCommand()
            setattr(payload, proto_field, value)
            pdata = payload.SerializeToString()

            packet  = ef_river3_pb2.River3SendHeaderMsg()
            message = packet.msg.add()
            message.src      = 32
            message.dest     = 2
            message.d_src    = 1
            message.d_dest   = 1
            message.cmd_func = 254
            message.cmd_id   = 17
            message.need_ack = 1
            message.data_len = len(pdata)
            message.seq      = 999900000 + random.randint(10000, 99999)
            message.pdata    = pdata

            return packet.SerializeToString()
        except Exception as exc:
            self.logger.error(f"[EcoFlow] River3 command build error: {exc}")
            return None

    def _build_delta3_command(self, proto_field, value, serial):
        """Build and return raw protobuf bytes for a Delta3 set command."""
        try:
            payload = ef_delta3_pb2.Delta3SetCommand()
            setattr(payload, proto_field, value)
            pdata = payload.SerializeToString()

            packet  = ef_delta3_pb2.Delta3SendHeaderMsg()
            message = packet.msg.add()
            message.src      = 32
            message.dest     = 2
            message.d_src    = 1
            message.d_dest   = 1
            message.cmd_func = 254
            message.cmd_id   = 17
            message.need_ack = 1
            message.data_len = len(pdata)
            message.seq      = 999900000 + random.randint(10000, 99999)
            message.pdata    = pdata

            return packet.SerializeToString()
        except Exception as exc:
            self.logger.error(f"[EcoFlow] Delta3 command build error: {exc}")
            return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gen_client_id(self):
        """Generate MQTT client ID in EcoFlow mobile app format: ANDROID_{UUID}_{userId}."""
        uid = _random_hex(32).upper()
        return f"ANDROID_{uid}_{self.user_id}"


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _random_hex(n):
    return "".join(random.choices("0123456789abcdef", k=n))


def _xor_decode(pdata, seq):
    """XOR each byte of pdata with the low byte of seq."""
    key = seq & 0xFF
    return bytes(b ^ key for b in pdata)


def _flatten_dict(d, parent_key="", sep="_"):
    """Recursively flatten a nested dict with underscore-joined keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def _extract_statistics(data, proto_module, enum_name):
    """
    Pull display_statistics_sum.list_info entries up to top-level dict keys.

    Each list_info item has {statistics_object: <enum>, statistics_content: <int>}.
    The enum name is e.g. STATISTICS_OBJECT_WATTH_IN_TOTAL — we strip the prefix
    and lowercase it to produce field-map-friendly keys like watth_in_total.

    proto_module: ef_river3_pb2 or ef_delta3_pb2
    enum_name:    "River3StatisticsObject" or "Delta3StatisticsObject"
    """
    try:
        stats_sum = data.get("display_statistics_sum", {})
        list_info = stats_sum.get("list_info", [])
        enum_cls  = getattr(proto_module, enum_name, None)
        for item in list_info:
            stat_obj     = item.get("statistics_object") or item.get("statisticsObject")
            stat_content = item.get("statistics_content") or item.get("statisticsContent")
            if stat_obj is None or stat_content is None:
                continue
            if isinstance(stat_obj, str) and stat_obj.startswith("STATISTICS_OBJECT_"):
                data[stat_obj.replace("STATISTICS_OBJECT_", "").lower()] = stat_content
            elif isinstance(stat_obj, int) and enum_cls is not None:
                try:
                    name = enum_cls.Name(stat_obj)
                    if name.startswith("STATISTICS_OBJECT_"):
                        data[name.replace("STATISTICS_OBJECT_", "").lower()] = stat_content
                except (ValueError, AttributeError):
                    pass
    except Exception:
        pass
    return data


def _mqtt_rc_desc(rc):
    desc = {
        1: "incorrect protocol version",
        2: "invalid client ID",
        3: "server unavailable",
        4: "bad username or password",
        5: "not authorised",
    }
    return desc.get(rc, f"unknown error {rc}")


def apply_field_map(flat_dict, device_type_id):
    """
    Map flat protobuf field dict to Indigo state updates.
    Returns list of {key, value, uiValue} dicts and a mirror dict.
    """
    field_map = DELTA3_FIELD_MAP if device_type_id == "ecoflowDelta3" else COMMON_FIELD_MAP
    kv     = []
    mirror = {}

    for proto_field, v in flat_dict.items():
        if proto_field not in field_map:
            continue
        state_id, cast, fmt = field_map[proto_field]

        # charging_state: special enum mapping
        if proto_field == "bms_chg_dsg_state":
            label = CHG_STATE_LABELS.get(int(v), "unknown")
            kv.append({"key": state_id, "value": label, "uiValue": label})
            mirror[state_id] = label
            continue

        # boolean fields
        if cast is bool:
            bval = bool(int(v)) if not isinstance(v, bool) else v
            kv.append({"key": state_id, "value": bval, "uiValue": str(bval)})
            mirror[state_id] = str(bval)
            continue

        # numeric fields
        try:
            typed = cast(v)
            ui    = fmt.replace("{v}", str(typed)) if fmt else str(typed)
            # handle float format strings like {v:.2f}
            if fmt and "{v:" in fmt:
                ui = fmt.replace("{v:", "{:").format(typed)
            kv.append({"key": state_id, "value": typed, "uiValue": ui})
            # mirror selected states
            if state_id in ("battery_soc", "power_in_w", "power_out_w",
                            "ac_out_w", "solar_in_w", "discharge_mins",
                            "ac_out_en", "dc_en"):
                mirror[state_id] = str(typed)
        except (ValueError, TypeError):
            pass

    return kv, mirror
