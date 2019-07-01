from enum import Enum, unique


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


ITEM_NAMES: list = [
    "Lock",
    "Log out",
    "Suspend",
    "Hibernate",
    "Restart",
    "Shut down",
]

ITEM_DESCRIPTIONS: list = [
    "Lock the session.",
    "Quit the session.",
    "Suspend to memory.",
    "Suspend to disk.",
    "Restart the machine.",
    "Shut down the machine.",
]

ITEM_ICONS: list = [
    "system-lock-screen",
    "system-log-out",
    "system-suspend",
    "system-suspend-hibernate",
    "system-reboot",
    "system-shutdown",
]

ITEM_ALIASES: list = [
    ["lock"],
    ["log out", "logout", "leave"],
    ["suspend", "sleep"],
    ["suspend", "hibernate"],
    ["restart", "reboot"],
    ["shut down", "shutdown", "poweroff", "halt"],
]

DESKTOP_ALIASES: dict = {
    Desktops.GNOME: ["Unity", "Pantheon", "GNOME"],
    Desktops.KDE: ["kde-plasma", "KDE"],
    Desktops.CINNAMON: ["X-Cinnamon", "Cinnamon"],
    Desktops.MATE: ["MATE"],
    Desktops.XFCE: ["XFCE"],
}
