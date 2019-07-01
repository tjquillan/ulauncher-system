from enum import Enum, unique
from typing import Dict, List


@unique
class Items(Enum):
    LOCK = 0
    LOGOUT = 1
    SUSPEND = 2
    HIBERNATE = 3
    REBOOT = 4
    POWEROFF = 5


@unique
class Desktops(Enum):
    GNOME = 0
    KDE = 1
    CINNAMON = 2
    MATE = 3
    XFCE = 4


ITEM_NAMES: List[str] = [
    "Lock",
    "Log out",
    "Suspend",
    "Hibernate",
    "Restart",
    "Shut down",
]

ITEM_DESCRIPTIONS: List[str] = [
    "Lock the session.",
    "Quit the session.",
    "Suspend to memory.",
    "Suspend to disk.",
    "Restart the machine.",
    "Shut down the machine.",
]

ITEM_ICONS: List[str] = [
    "system-lock-screen",
    "system-log-out",
    "system-suspend",
    "system-suspend-hibernate",
    "system-reboot",
    "system-shutdown",
]

ITEM_ALIASES: List[List[str]] = [
    ["lock"],
    ["log out", "logout", "leave"],
    ["suspend", "sleep"],
    ["suspend", "hibernate"],
    ["restart", "reboot"],
    ["shut down", "shutdown", "poweroff", "halt"],
]

DESKTOP_ALIASES: Dict[Desktops, List[str]] = {
    Desktops.GNOME: ["Unity", "Pantheon", "GNOME"],
    Desktops.KDE: ["kde-plasma", "KDE"],
    Desktops.CINNAMON: ["X-Cinnamon", "Cinnamon"],
    Desktops.MATE: ["MATE"],
    Desktops.XFCE: ["XFCE"],
}
