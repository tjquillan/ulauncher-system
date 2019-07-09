import json
import logging
import os

from typing import Dict, List

import gi

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort:skip # noqa: E261

logger: logging.Logger = logging.getLogger(__name__)


class Entry():
    def __init__(self, data: dict, desktop: str, icon_theme: Gtk.IconTheme):
        def get_icon(name) -> str:
            icon: Gtk.IconInfo = icon_theme.lookup_icon(
                name, 32, Gtk.IconLookupFlags.GENERIC_FALLBACK
            )

            if icon:
                return icon.get_filename()
            else:
                logger.warning("No icon found for: {}".format(name))
                return ""

        self.__name: str = data["name"]
        self.__description: str = data["description"]
        self.__icon: str = get_icon(data["icon"])
        self.__aliases: List[str] = data["aliases"]
        self.__command: str = data["commands"][desktop] or data["commands"]["default"]

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


class EntryIndex():
    def __init__(self):
        def get_desktop(desktops: dict) -> str:
            current_desktop = os.environ.get("XDG_CURRENT_DESKTOP")

            for desktop in desktops.keys():
                if any(current_desktop in s for s in desktops[desktop]):
                    return desktop

            return "default"

        data = json.load(open("data.json"))
        desktop: str = get_desktop(data["desktops"])
        icon_theme: Gtk.IconTheme = Gtk.IconTheme.get_default()

        self.__entries: Dict[str, Entry] = {
            entry: Entry(data["entries"][entry], desktop, icon_theme)
            for entry in data["entries"].keys()
            if Entry(data["entries"][entry], desktop, icon_theme).command
        }
        self.__aliases: List[List[str]] = [
            entry.aliases
            for entry in self.__entries.values()
        ]

    def get_entry(self, id) -> Entry:
        return self.__entries[id]

    @property
    def entries(self) -> Dict[str, Entry]:
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
            for entry in self.__entries.entries.values()
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
