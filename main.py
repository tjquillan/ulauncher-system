import logging
import os

from typing import Dict, List, Optional

import gi

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from constants import (
    DESKTOP_ALIASES,
    ITEM_ALIASES,
    ITEM_DESCRIPTIONS,
    ITEM_ICONS,
    ITEM_NAMES,
    Desktops,
    Items,
)


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort:skip # noqa: E261

logger: logging.Logger = logging.getLogger(__name__)


class SystemExtension(Extension):
    def __init__(self):
        super(SystemExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def __init__(self):
        icon_theme: Gtk.IconTheme = Gtk.IconTheme.get_default()
        commands: Dict[Items, Optional[str]] = get_commands()
        self._items: Dict[Items, ExtensionResultItem] = {
            item: ExtensionResultItem(
                icon=get_icon(ITEM_ICONS[item.value], icon_theme),
                name=ITEM_NAMES[item.value],
                description=ITEM_DESCRIPTIONS[item.value],
                on_enter=RunScriptAction(commands[item]),
            )
            for item in Items
        }

    def on_event(self, event: KeywordQueryEvent, extension):
        arg: str = event.get_argument()
        if arg:
            items: List[ExtensionResultItem] = []
            for aliases in ITEM_ALIASES:
                if any(arg in s for s in aliases):
                    items.append(self._items[Items(aliases.index(aliases))])
            return RenderResultListAction(items)
        else:
            return RenderResultListAction([item for item in self._items.values()])


def get_icon(name: str, icon_theme) -> str:
    icon: Gtk.IconInfo = icon_theme.lookup_icon(
        name, 32, Gtk.IconLookupFlags.GENERIC_FALLBACK
    )

    if icon:
        return icon.get_filename()
    else:
        logger.warning("No icon found for: {}".format(name))
        return ""


def get_commands() -> Dict[Items, Optional[str]]:
    commands: Dict[Items, Optional[str]] = {
        Items.LOCK: "xdg-screensaver lock",
        Items.LOGOUT: "pkill -u $USER",
        Items.SUSPEND: "systemctl suspend -i",
        Items.HIBERNATE: "systemctl hibernate -i",
        Items.REBOOT: "systemctl reboot -i",
        Items.POWEROFF: "systemctl poweroff -i",
    }

    current_desktop: str = os.environ.get("XDG_CURRENT_DESKTOP")

    desktop_type: Desktops = None
    for desktop in DESKTOP_ALIASES:
        if any(current_desktop in s for s in DESKTOP_ALIASES[desktop]):
            desktop_type = desktop
            break

    if desktop_type is Desktops.GNOME:
        commands[Items.LOCK] = "gnome-screensaver-command --lock"
        commands[Items.LOGOUT] = "gnome-session-quit --logout"
        commands[Items.REBOOT] = "gnome-session-quit --reboot"
        commands[Items.POWEROFF] = "gnome-session-quit --power-off"
    elif desktop_type is Desktops.KDE:
        commands[
            Items.LOCK
        ] = "dbus-send --dest=org.freedesktop.ScreenSaver --type=method_call /ScreenSaver org.freedesktop.ScreenSaver.Lock"
        commands[Items.LOGOUT] = "qdbus org.kde.ksmserver /KSMServer logout 0 0 0"
        commands[Items.REBOOT] = "qdbus org.kde.ksmserver /KSMServer logout 0 1 0"
        commands[Items.POWEROFF] = "qdbus org.kde.ksmserver /KSMServer logout 0 2 0"
    elif desktop_type is Desktops.CINNAMON:
        commands[Items.LOCK] = "cinnamon-screensaver-command --lock"
        commands[Items.LOGOUT] = "cinnamon-session-quit --logout"
        commands[Items.REBOOT] = "cinnamon-session-quit --reboot"
        commands[Items.POWEROFF] = "cinnamon-session-quit --power-off"
    elif desktop_type is Desktops.MATE:
        commands[Items.LOCK] = "mate-screensaver-command --lock"
        commands[Items.LOGOUT] = "mate-session-save --logout-dialog"
        commands[
            Items.SUSPEND
        ] = 'sh -c "mate-screensaver-command --lock && systemctl suspend -i"'
        commands[
            Items.HIBERNATE
        ] = 'sh -c "mate-screensaver-command --lock && systemctl hibernate -i"'
        commands[Items.REBOOT] = "mate-session-save --shutdown-dialog"
        commands[Items.POWEROFF] = "mate-session-save --shutdown-dialog"
    elif desktop_type is Desktops.XFCE:
        commands[Items.LOCK] = "xflock4"
        commands[Items.LOGOUT] = "xfce4-session-logout --logout"
        commands[Items.SUSPEND] = "xfce4-session-logout --suspend"
        commands[Items.HIBERNATE] = "xfce4-session-logout --hibernate"
        commands[Items.REBOOT] = "xfce4-session-logout --reboot"
        commands[Items.POWEROFF] = "xfce4-session-logout --halt"

    return commands


if __name__ == "__main__":
    SystemExtension().run()
