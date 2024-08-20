#!/usr/bin/env python
# coding: utf8

"""
krunner source code repo: https://github.com/KDE/krunner

https://develop.kde.org/docs/plasma/krunner/

krunner5 package
methods: /usr/share/dbus-1/interfaces/kf5_org.kde.krunner1.xml
"""

import logging
import subprocess

# arch python-dbus
# dbus-python=1.3.2 python-dbus-command=1.3.2
# optional: python-gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject, GLib

logging.basicConfig(
    level=logging.INFO,
    filename="/tmp/next-runner.log",
    format="%(asctime)s - %(filename)s - %(lineno)s - %(message)s",
)
log = logging.getLogger(__name__)


log.info(f'{"*" * 20} starting the runner ...')

DBusGMainLoop(set_as_default=True)

OBJPATH = "/next"
IFACE = "org.kde.krunner1"
SERVICE = "xyz.simple-is-better.next"

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
        if query.startswith("al"):
            results += [
                (
                    "alacritty",
                    "Alacritty",
                    "utilities-terminal",
                    100,
                    1,
                    {"subtext": "Alacritty Terminal"},
                )
            ]
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
            "run, received a Run command, match_id: %s, action_id: %s, args: %s, kwargs: %s",
            match_id,
            action_id,
            args,
            kwargs,
        )
        if match_id == "wez-theme":
            subprocess.run(["touch", "-h", "/home/maple/.config/wezterm/wezterm.lua"])
            log.info("touched")

        if match_id == "alacritty":
            values = match_id.split(":", maxsplit=1)
            log.info("get values: %s", values)

            hostname = "ss-dev"
            command, args = "alacritty", ["--command", "ssh", hostname]
            if self.launch_application(command, args):
                self.send_desktop_notification(
                    "Alacritty 已启动", f"已连接到 {hostname}"
                )

    def is_dbus_service_available(self, service_name):
        try:
            bus = dbus.SessionBus()
            bus.get_name_owner(service_name)
            return True
        except dbus.exceptions.DBusException:
            return False

    def launch_application_via_dbus(self, app_name: str, args: list):
        """通过 DBus 启动应用程序"""
        log.info(f"正在通过 DBus 启动 {app_name}，参数：{args}")

        try:
            bus = dbus.SessionBus()
            obj = bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
            interface = dbus.Interface(obj, "org.freedesktop.DBus")

            app_dbus_name = f"org.freedesktop.Application.{app_name}"
            if not self.is_dbus_service_available(app_dbus_name):
                raise dbus.exceptions.DBusException("DBus service not available")

            app_dbus_name = interface.GetNameOwner(app_dbus_name)
            app_obj = bus.get_object(app_dbus_name, "/org/freedesktop/Application")
            app_interface = dbus.Interface(app_obj, "org.freedesktop.Application")

            app_interface.Activate(
                dbus.Dictionary(
                    {"desktop-startup-id": "", "args": dbus.Array(args, signature="s")},
                    signature="sv",
                )
            )

            log.info(f"{app_name} 成功通过 DBus 启动")
            return True
        except dbus.exceptions.DBusException as e:
            log.error(f"通过 DBus 启动 {app_name} 失败: {str(e)}")
            return False

    def launch_application_via_subprocess(self, app_name: str, args: list):
        """使用 subprocess 启动应用程序"""
        log.info(f"正在通过 subprocess 启动 {app_name}，参数：{args}")
        try:
            full_command = [app_name] + args
            subprocess.Popen(
                full_command,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            log.info(f"{app_name} 成功通过 subprocess 启动")
            self.send_desktop_notification(f"{app_name} 已启动", f"参数：{args}")
            return True
        except Exception as e:
            log.error(f"通过 subprocess 启动 {app_name} 失败: {str(e)}")
            return False

    def launch_application(self, app_name: str, args: list):
        """尝试通过 DBus 启动应用程序，如果失败则使用 subprocess"""
        if not self.launch_application_via_dbus(app_name, args):
            return self.launch_application_via_subprocess(app_name, args)
        return True

    @dbus.service.method(IFACE)
    def Teardown(self, *args, **kwargs):
        # this session is done
        log.info("done, %s, %s", args, kwargs)

    def send_desktop_notification(self, summary: str, body: str, icon: str = ""):
        """
        使用 DBus 发送桌面通知

        :param summary: 通知的标题
        :param body: 通知的详细内容
        :param icon: 通知的图标（可选）
        """
        try:
            bus = dbus.SessionBus()
            notify_object = bus.get_object(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            )
            notify_interface = dbus.Interface(
                notify_object, "org.freedesktop.Notifications"
            )

            notify_interface.Notify(
                "Next Runner",  # 应用名称
                0,  # 替换 ID （0 表示新通知）
                icon,  # 图标
                summary,  # 标题
                body,  # 内容
                [],  # 动作
                {},  # 提示
                -1,  # 超时（-1 表示使用系统默认值）
            )
            log.info(f"已发送桌面通知: {summary}")
        except dbus.exceptions.DBusException as e:
            log.error(f"发送桌面通知失败: {str(e)}")


runner = Runner()

loop = GLib.MainLoop()
loop.run()
