import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort:skip # noqa: E402

from ulauncher.api.client.EventListener import EventListener  # noqa: E402
from ulauncher.api.client.Extension import Extension  # noqa: E402
from ulauncher.api.shared.action.RenderResultListAction import (  # noqa: E402
    RenderResultListAction,
)
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction  # noqa: E402
from ulauncher.api.shared.event import KeywordQueryEvent  # noqa: E402
from ulauncher.api.shared.item.ExtensionResultItem import (  # noqa: E402
    ExtensionResultItem,
)

logger: logging.Logger = logging.getLogger(__name__)

ULAUNCHER_SYSTEM_DIR = os.path.dirname(__file__)
USER_HOME_DIR = os.path.expanduser("~")
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", f"{USER_HOME_DIR}/.config")
USER_CONFIG_DIR = f"{XDG_CONFIG_HOME}/ulauncher-system"

class Entry:
    __slots__: List[str] = [
        "__name",
        "__description",
        "__icon",
        "__icon_theme",
        "__aliases",
        "__command",
    ]

    def __init__(self, data: Dict[str, Any], icon_theme: Gtk.IconTheme):
        self.__icon_theme: Gtk.IconTheme = icon_theme
        try:
            self.__name: str = data["name"]
            self.__description: str = data["description"]
            self.__icon: str = self.__get_icon(data["icon"])
            self.__aliases: List[str] = data["aliases"]
            self.__command: str = data["command"]
        except KeyError as e:
            raise Exception(f"{e} not found in data")

    def __get_icon(self, icon_name: str) -> str:
        icon: Gtk.IconInfo = self.__icon_theme.lookup_icon(
            icon_name, 32, Gtk.IconLookupFlags.GENERIC_FALLBACK
        )

        if icon:
            return icon.get_filename()
        else:
            logger.warning(f"No icon found for: {icon_name}")
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


def get_desktops(file_path: str) -> Dict[str, Dict[str, Any]]:
    desktops: Dict[str, Dict[str, Any]] = json.load(open(f"{file_path}/desktops.json"))
    user_desktops_path = Path(f"{USER_CONFIG_DIR}/desktops.json")
    if user_desktops_path.exists():
        user_desktops = json.load(user_desktops_path.open())
        for desktop in user_desktops:
            desktops[desktop] = user_desktops[desktop]
    return desktops


def get_desktop(desktops: Dict[str, Dict[str, Any]]) -> Optional[str]:
    for desktop_key in desktops:
        desktop = desktops[desktop_key]

        env_var: Optional[str] = os.environ.get(desktop["env"])
        if env_var:
            try:
                if any(env_var in s for s in desktop["aliases"]):
                    return desktop_key
            except KeyError:
                return desktop_key
    return None


class EntryIndex:
    __slots__: List[str] = ["__entries", "__aliases"]

    def __init__(self):
        file_path: str = os.path.dirname(os.path.realpath(__file__))

        entries: Dict[str, Dict[str, str]] = json.load(
            open(f"{file_path}/entries/default.json")
        )
        desktop: Optional[str] = get_desktop(get_desktops(file_path))

        def update_entries(path_str: str):
            path: Path = Path(path_str)
            if path.exists():
                desktop_entries: Dict[str, Optional[Dict[str, str]]] = json.load(
                    path.open()
                )
                for entry_key in desktop_entries:
                    entry = desktop_entries[entry_key]
                    if entry is None:
                        # Remove the key from entries if it exists
                        entries.pop(entry_key, None)
                    elif entry_key not in entries:
                        entries[entry_key] = entry
                    else:
                        entries[entry_key].update(entry)

        if desktop:
            update_entries(f"{file_path}/entries/{desktop}.json")

        update_entries(f"{USER_CONFIG_DIR}/entries/default.json")

        if desktop:
            update_entries(f"{USER_CONFIG_DIR}/entries/{desktop}.json")

        icon_theme: Gtk.IconTheme = Gtk.IconTheme.get_default()
        icon_theme.append_search_path(f"{ULAUNCHER_SYSTEM_DIR}/images")
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

    def on_event(self, event: KeywordQueryEvent, _) -> RenderResultListAction:
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
