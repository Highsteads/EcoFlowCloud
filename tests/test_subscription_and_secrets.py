#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:    test_subscription_and_secrets.py
# Description: Regression tests for 1.11 — the MQTT subscription follows the
#              configured devices without a reconnect, and each IndigoSecrets
#              key is read on its own.
# Author:      CliveS & Claude Opus 5.5
# Date:        27-09-2026
# Version:     1.0
#
# No hardware and no network: paho, requests, indigo, plugin_utils and
# IndigoSecrets are all stubbed, so the real IndigoSecrets.py on this Mac is
# never read. The MQTT client object is a recorder.

import ast
import importlib.util
import logging
import os
import sys
import types

import pytest

REPO       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_DIR = os.path.join(REPO, "EcoFlowCloud.indigoPlugin", "Contents", "Server Plugin")


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class FakeMqtt:
    """Records what the client asks the broker to do."""

    def __init__(self):
        self.subscribed   = []
        self.unsubscribed = []

    def subscribe(self, topic, qos=0):
        self.subscribed.append(topic)

    def unsubscribe(self, topic):
        self.unsubscribed.append(topic)


class FakeDevice:
    def __init__(self, dev_id, serial, type_id="ecoflowRiver3", enabled=True):
        self.id           = dev_id
        self.name         = f"Device {dev_id}"
        self.deviceTypeId = type_id
        self.enabled      = enabled
        self.configured   = True
        self.pluginProps  = {"serial_number": serial}
        self.states       = {}

    def stateListOrDisplayStateIdChanged(self):
        pass

    def updateStateOnServer(self, key, value):
        self.states[key] = value


class FakeDevices:
    def __init__(self):
        self.devs = []

    def iter(self, _filter=None):
        return list(self.devs)


class _PluginBase:
    class StopThread(Exception):
        pass

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        self.pluginId           = pluginId
        self.pluginPrefs        = pluginPrefs
        self.logger             = logging.getLogger("ecoflow-test")
        self.indigo_log_handler = logging.NullHandler()


def _module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def _load(path, name, stubs):
    """Exec a source file as a fresh module with the given sys.modules stubs."""
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value


def _load_client_module():
    paho        = _module("paho")
    paho_mqtt   = _module("paho.mqtt")
    paho_client = _module("paho.mqtt.client", MQTT_ERR_SUCCESS=0)
    paho.mqtt, paho_mqtt.client = paho_mqtt, paho_client
    stubs = {
        "paho": paho, "paho.mqtt": paho_mqtt, "paho.mqtt.client": paho_client,
        "requests": _module("requests"),
    }
    return _load(os.path.join(SERVER_DIR, "ecoflow_client.py"), "ecoflow_client_under_test", stubs)


def _load_plugin_module(secrets):
    """secrets: dict of names the stub IndigoSecrets module defines."""
    client_mod = _load_client_module()
    indigo = _module("indigo", PluginBase=_PluginBase, devices=FakeDevices(), Dict=dict)
    stubs = {
        "indigo":         indigo,
        "plugin_utils":   _module("plugin_utils"),
        "IndigoSecrets":  _module("IndigoSecrets", **secrets),
        "ecoflow_client": client_mod,
    }
    mod = _load(os.path.join(SERVER_DIR, "plugin.py"), "ecoflow_plugin_under_test", stubs)
    return mod, indigo, client_mod


def _make_client(client_mod, serial_to_type, connected=True):
    client = client_mod.EcoFlowClient(
        api_host="api.example.com", email="", password="",
        on_message_cb=lambda *a: None, on_connect_cb=lambda *a: None,
        logger=logging.getLogger("ecoflow-test"),
    )
    client._serial_to_type = dict(serial_to_type)
    client._mqtt           = FakeMqtt()
    client.connected       = connected
    client.polled          = []
    client.request_quota   = lambda serial=None: client.polled.append(serial)
    return client


@pytest.fixture
def plugin_env():
    mod, indigo, client_mod = _load_plugin_module({})
    plugin = mod.Plugin("com.clives.indigoplugin.ecoflowcloud", "EcoFlow Cloud", "1.11", {})
    return plugin, indigo, client_mod


# ---------------------------------------------------------------------------
# Subscription follows the devices
# ---------------------------------------------------------------------------

def test_device_added_while_connected_is_subscribed_and_polled(plugin_env):
    plugin, indigo, client_mod = plugin_env
    first  = FakeDevice(1, "SN-FIRST")
    second = FakeDevice(2, "SN-SECOND", type_id="ecoflowDelta3")
    indigo.devices.devs = [first]
    plugin.client = _make_client(client_mod, {"SN-FIRST": "ecoflowRiver3"})

    indigo.devices.devs.append(second)
    plugin.deviceStartComm(second)

    assert plugin.client._mqtt.subscribed == ["/app/device/property/SN-SECOND"]
    assert plugin.client._mqtt.unsubscribed == []
    assert plugin.client.polled == ["SN-SECOND"]
    assert plugin.client._serial_to_type == {
        "SN-FIRST": "ecoflowRiver3", "SN-SECOND": "ecoflowDelta3"}


def test_serial_number_change_moves_the_subscription(plugin_env):
    plugin, indigo, client_mod = plugin_env
    dev = FakeDevice(1, "SN-OLD")
    indigo.devices.devs = [dev]
    plugin.client = _make_client(client_mod, {"SN-OLD": "ecoflowRiver3"})

    dev.pluginProps["serial_number"] = "SN-NEW"
    plugin.deviceStartComm(dev)   # Indigo restarts the device on a serial change

    assert plugin.client._mqtt.subscribed == ["/app/device/property/SN-NEW"]
    assert plugin.client._mqtt.unsubscribed == ["/app/device/property/SN-OLD"]
    assert plugin.client._serial_to_type == {"SN-NEW": "ecoflowRiver3"}


def test_started_device_counts_even_if_device_list_shows_old_props(plugin_env):
    plugin, indigo, client_mod = plugin_env
    listed  = FakeDevice(1, "SN-OLD")
    started = FakeDevice(1, "SN-NEW")
    indigo.devices.devs = [listed]
    plugin.client = _make_client(client_mod, {"SN-OLD": "ecoflowRiver3"})

    plugin.deviceStartComm(started)

    assert "/app/device/property/SN-NEW" in plugin.client._mqtt.subscribed


def test_restarting_a_known_device_changes_nothing(plugin_env):
    plugin, indigo, client_mod = plugin_env
    dev = FakeDevice(1, "SN-FIRST")
    indigo.devices.devs = [dev]
    plugin.client = _make_client(client_mod, {"SN-FIRST": "ecoflowRiver3"})

    plugin.deviceStartComm(dev)

    assert plugin.client._mqtt.subscribed == []
    assert plugin.client._mqtt.unsubscribed == []
    assert plugin.client.polled == []


def test_no_client_yet_brings_the_next_connect_forward(plugin_env):
    plugin, indigo, _ = plugin_env
    dev = FakeDevice(1, "SN-FIRST")
    indigo.devices.devs = [dev]
    plugin.client        = None
    plugin._reconnect_at = 10 ** 12

    plugin.deviceStartComm(dev)

    assert plugin._reconnect_at == 0


def test_set_devices_while_disconnected_waits_for_on_connect():
    client_mod = _load_client_module()
    client = _make_client(client_mod, {"SN-FIRST": "ecoflowRiver3"}, connected=False)

    added, removed = client.set_devices({"SN-FIRST": "ecoflowRiver3", "SN-SECOND": "ecoflowRiver3"})

    assert (added, removed) == (["SN-SECOND"], [])
    assert client._mqtt.subscribed == []

    # When the connection comes up, _on_connect subscribes the whole map.
    broker = FakeMqtt()
    client._on_connect(broker, None, None, 0)
    assert sorted(broker.subscribed) == ["/app/device/property/SN-FIRST",
                                         "/app/device/property/SN-SECOND"]


# ---------------------------------------------------------------------------
# IndigoSecrets keys are independent
# ---------------------------------------------------------------------------

def test_file_with_only_the_email_keeps_the_email():
    mod, _, _ = _load_plugin_module({"ECOFLOW_EMAIL": "file@example.com"})
    assert mod.ECOFLOW_EMAIL == "file@example.com"
    assert mod.ECOFLOW_PASSWORD == ""

    plugin = mod.Plugin("id", "EcoFlow Cloud", "1.11",
                        {"ecoflow_email": "dialog@example.com", "ecoflow_password": "dialog-pw"})
    assert plugin.email == "file@example.com"
    assert plugin.password == "dialog-pw"


def test_file_with_only_the_password_keeps_the_password():
    mod, _, _ = _load_plugin_module({"ECOFLOW_PASSWORD": "file-pw"})
    assert mod.ECOFLOW_EMAIL == ""
    assert mod.ECOFLOW_PASSWORD == "file-pw"

    plugin = mod.Plugin("id", "EcoFlow Cloud", "1.11",
                        {"ecoflow_email": "dialog@example.com", "ecoflow_password": "dialog-pw"})
    assert plugin.email == "dialog@example.com"
    assert plugin.password == "file-pw"


def test_bundled_secrets_template_carries_both_ecoflow_keys_blank():
    path = os.path.join(SERVER_DIR, "IndigoSecrets_example.py")
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    values = {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }
    assert values.get("ECOFLOW_EMAIL") == ""
    assert values.get("ECOFLOW_PASSWORD") == ""
