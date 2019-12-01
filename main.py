import json
import logging
import os

from pathlib import Path
from typing import Dict, List, Optional

import gi
import xdg

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort:skip # noqa: E261

logger: logging.Logger = logging.getLogger(__name__)


class Entry:
    __slots__: List[str] = [
        "__name",
        "__description",
        "__icon",
        "__icon_theme",
        "__aliases",
        "__command",
    ]

    def __init__(self, data: dict, icon_theme: Gtk.IconTheme):
        self.__name: str = data["name"]
        self.__description: str = data["description"]
        self.__icon_theme: Gtk.IconTheme = icon_theme
        self.__icon: str = self.__get_icon(data["icon"])
        self.__aliases: List[str] = data["aliases"]
        self.__command: str = data["command"]

    def __get_icon(self, icon_name: str) -> str:
        icon: Gtk.IconInfo = self.__icon_theme.lookup_icon(
            icon_name, 32, Gtk.IconLookupFlags.GENERIC_FALLBACK
        )

        if icon:
            return icon.get_filename()
        else:
            logger.warning("No icon found for: {}".format(icon_name))
            return ""

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description

    @property
    def icon(self) -> str:
        return self.__icon

    @property
    def aliases(self) -> List[str]:
        return self.__aliases

    @property
    def command(self) -> str:
        return self.__command


class EntryIndex:
    __slots__: List[str] = ["__entries", "__aliases"]

    def __init__(self):
        def get_desktop(desktops: dict) -> Optional[str]:
            for desktop_key in desktops:
                desktop = desktops[desktop_key]

                env_var: Optional[str] = os.environ.get(desktop["env"])
                if desktop["aliases"]:
                    if any(env_var in s for s in desktop["aliases"]):
                        return desktop_key
                else:
                    if env_var:
                        return desktop_key
            return None

        file_path: str = os.path.dirname(os.path.realpath(__file__))

        entries: dict = json.load(open(f"{file_path}/entries/default.json"))
        desktop: Optional[str] = get_desktop(
            json.load(open(f"{file_path}/desktops.json"))
        )

        def update_entries(new_entries):
            for entry_key in new_entries.keys():
                for value_key in new_entries[entry_key].keys():
                    if entry_key not in entries:
                        entries[entry_key] = {}
                    entries[entry_key][value_key] = new_entries[entry_key][value_key]

        if desktop and Path(f"{file_path}/entries/{desktop}.json").exists():
            desktop_entries: Dict[dict] = json.load(
                open(f"{file_path}/entries/{desktop}.json")
            )
            update_entries(desktop_entries)

        if Path(f"{xdg.BaseDirectory.xdg_config_home}/ulauncher-system.json").exists():
            user_entries = json.load(
                open(f"{xdg.BaseDirectory.xdg_config_home}/ulauncher-system.json")
            )
            update_entries(user_entries)

        logger.error(entries.keys())

        icon_theme: Gtk.IconTheme = Gtk.IconTheme.get_default()
        self.__entries: List[Entry] = [
            Entry(entry, icon_theme) for entry in entries.values() if entry["command"]
        ]
        self.__aliases: List[List[str]] = [entry.aliases for entry in self.__entries]

    @property
    def entries(self) -> List[Entry]:
        return self.__entries

    @property
    def aliases(self) -> List[List[str]]:
        return self.__aliases


class SystemExtension(Extension):
    def __init__(self):
        super(SystemExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def __init__(self):
        self.__entries: EntryIndex = EntryIndex()
        self.__result_items: List[ExtensionResultItem] = [
            ExtensionResultItem(
                icon=entry.icon,
                name=entry.name,
                description=entry.description,
                on_enter=RunScriptAction(entry.command),
            )
            for entry in self.__entries.entries
        ]

    def on_event(self, event: KeywordQueryEvent, extension):
        arg: str = event.get_argument()
        if arg:
            return RenderResultListAction(
                [
                    self.__result_items[self.__entries.aliases.index(aliases)]
                    for aliases in self.__entries.aliases
                    if any(arg in s for s in aliases)
                ]
            )
        else:
            return RenderResultListAction(self.__result_items)


if __name__ == "__main__":
    SystemExtension().run()
