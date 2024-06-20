#!/usr/bin/env python
# coding: utf8

"""
krunner source code repo: https://github.com/KDE/krunner

https://develop.kde.org/docs/plasma/krunner/

krunner5 package
methods: /usr/share/dbus-1/interfaces/kf5_org.kde.krunner1.xml
"""

from datetime import datetime
import dbus
import dbus.service
import libvirt
import subprocess
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import logging

logging.basicConfig(
    level=logging.INFO,
    filename="/tmp/x-runner.log",
    format="%(asctime)s - %(filename)s - %(lineno)s - %(message)s",
)
log = logging.getLogger(__name__)


log.info(f'{"*" * 20} starting the runner ...')

DBusGMainLoop(set_as_default=True)

OBJPATH = "/xg"
IFACE = "org.kde.krunner1"
SERVICE = "space.myctl.my-runner"

VMM_PATH = "/usr/share/virt-manager/"
ICONS_PATH = VMM_PATH + "icons/hicolor/22x22/status/"
RUNNING_ICON = ICONS_PATH + "state_running.png"
DEFAULT_ICON = ICONS_PATH + "state_shutoff.png"


class Runner(dbus.service.Object):
    """Communicate with KRunner, deal with queries, provide and run actions."""

    def __init__(self) -> None:
        """Create dbus service"""
        dbus.service.Object.__init__(
            self, dbus.service.BusName(SERVICE, dbus.SessionBus()), OBJPATH
        )

        log.info("__init__, initializing ...")
        self.hosts = [
            "a34",
            "n33",
            "n35",
            "bpi",
            "rpi",
            "joe",
            "acer",
            "ali",
            "ss-dev",
            "mi2",
        ]

    @dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
    def Match(self, query: str):
        """This method is used to get the matches and it returns a list of tuples"""
        log.info("==== Received a Match: [%s]", query)

        # [(ID, Text, IconName, Type (Plasma::QueryType), Relevance(0-1), Properties (subtext, category and urls))]
        # - ID
        # - Text
        # - IconName: kde 找到 Icons - System Settings, 可以找到現在使用的 icon 主題, 比如 "Breeze Dark", yay -Qil breeze-icons
        # - Type
        # - Relevance
        # - Properties (VariantMap)
        #    - urls (StringList)
        #    - category
        #    - subtext
        #    - actions (StringList of RemoteAction's IDs). In case you don't want to display any actions set this to an empty list.
        #      Otherwise all the actions will be shown for compatibility with the previous versions of the D-Bus API.
        #      When the actions only need to be fetched once you can set the X-Plasma-Request-Actions-Once property of
        #      the service file to true.
        #    - icon-data (iiibiiay). Custom icon pixmap. Icon name should be preferred, if available.
        #      Format is the same as org.freedesktop.Notifications icon-data, in order: width, height, row stride,
        #      has alpha, bits per sample, number of channels, pixmap data.
        #    - multiline (boolean). If the text should be displayed as styled multiline text.

        log.info("matches by (ID, Text, IconName, Type, Relevance, Properties)")

        results = []
        if query.startswith("wez") or "color" in query:
            log.info("wez theme updating request")
            results += [
                (
                    "wez-theme",
                    "Wezterm Colorscheme",
                    "user-busy-symbolic",
                    100,
                    1,
                    {"subtext": "Update Wez Theme", "actions": ["start"]},
                )
            ]

        for hostname in self.hosts:
            if hostname in query:
                results += [
                    (
                        f"wezterm:{hostname}",
                        f"wezterm connect {hostname}",
                        "user-busy-symbolic",
                        100,
                        0,
                        {"subtext": ""},
                    ),
                    (
                        f"alacritty:{hostname}",
                        f"alacritty ssh {hostname}",
                        "user-busy-symbolic",
                        100,
                        1,
                        {"subtext": f"alacritty ssh {hostname}"},
                    ),
                ]

        if query.startswith("wez"):
            results = results + [
                (
                    hostname,
                    f"wez to {hostname}",
                    "user-busy-symbolic",
                    100,
                    rel / 10,
                    {"subtext": "SubText"},
                )
                for rel, hostname in enumerate(self.hosts)
            ]
        log.info("match results: %s", results)
        return results

    @dbus.service.method(IFACE, out_signature="a(sss)")
    def Actions(self):
        """
        Returns a list of actions supported by this runner.
        For example, a song match returned by a music player runner can be queued, added to the playlist, or played.
        This should be constant
        Structure is:
          - ID
          - Text
          - IconName
        """
        log.info(
            f"{'+' * 10} actions, Received an Actions query, called upon initialization"
        )
        # ID, Text, IconName
        return [
            ("start", "Start the VM", "media-playback-start"),
            # ("stop", "Stop the VM", "media-playback-stop"),
            # ("kill", "ss-dev", "user-busy-symbolic"),
        ]

    @dbus.service.method(IFACE, in_signature="ss")
    def Run(self, match_id: str, action_id: str, *args, **kwargs):
        # match_id is the ID for `Match` record
        # action_id: The action ID to run. For the default action this will be empty, the ID from `Actions` method
        log.info(
            "run, received a Run command, match_id: %s, action_id: %s, %s, %s",
            match_id,
            action_id,
            args,
            kwargs,
        )
        if match_id == "wez-theme":
            subprocess.run(["touch", "-h", "/home/maple/.config/wezterm/wezterm.lua"])
            log.info("touched")

        if match_id.startswith("alacritty:"):
            hostname = match_id.split(":")[1]
            subprocess.run(["alacritty", "-e", "ssh", hostname])
            log.info("alacritty ssh to %s", hostname)

    @dbus.service.method(IFACE)
    def Teardown(self, *args, **kwargs):
        # this session is done
        log.info("done, %s, %s", args, kwargs)


runner = Runner()

loop = GLib.MainLoop()
loop.run()
