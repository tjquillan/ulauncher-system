# Ulauncher-System

This is a extension for [Ulauncher](https://ulauncher.io/) that allows you to:

* Lock
* Log Off
* Suspend
* Hibernate
* Reboot
* Shutdown
* Reboot to Bios

## What sets it appart?

* It will attempt to work nicely with the Desktop Environment of you choice. Below are the currently supported DEs.
  If one of these is not detected default commands will be used if possible.
  * GNOME Based (Unity, Gnome, Etc.)
  * KDE
  * Cinnamon
  * Mate
  * XFCE
* It uses the system icon theme for all but its required icon.
* It is extremely configurable
* More in the future!

## Configuration

Every part of ulauncher-system is configurable. You can change and add new desktops to be detected and you can change and add commands for those desktops.

Configurations are stored in `$XDG_CONFIG_HOME/ulauncher-system`. When `$XDG_CONFIG_HOME` is not defined it will default to `$HOME/.config` according to the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)

### Configuration Load Order

1. Default
2. Desktop
3. User Default
4. User Desktop

### Changing and Adding Desktops

To change and add desktops you will be editing: `$XDG_CONFIG_HOME/ulauncher-system/desktops.json`

There are two ways to declare a desktop

1. By specifing an environment variable to check

    Use this when the existence of the variable is exclusive to the current desktop.

    **Example**

    ```json
    "sway": {
        "env": "SWAYSOCK"
    }
    ```

2. By specifing an environment variable to check and valid aliases of it

    Use this when the variable contains information that specifies the current desktop.

    **Example**

    ```json
    "kde": {
        "env": "XDG_CURRENT_DESKTOP",
        "aliases": ["kde-plasma", "KDE"]
    },
    ```

### Changing and Adding to Desktop Entries

To change and add desktop entries you will need to add files to `$XDG_CONFIG_HOME/ulauncher-system/entries/` in the form of `<desktop_key>.json`, with `<desktop_key>` being the key of the desktop as specified in `desktop.json`, or `default.json` for desktop agnostic configuration. For examples of these see [default.json](https://github.com/iboyperson/ulauncher-system/blob/master/entries/default.json).

If you are using any of the keys defined in `default.json` you only need to define the values you want to override in your user copy. However, if you are adding a new key you must specify all the values.

To disable an entry simply put `<key>: null` in your config.

#### Values

* `<key>`: A unique identifier
  * `name`: The name to be displayed in Ulauncher
  * `description`: The description to be displayed in Ulauncher
  * `icon`: The icon name of the icon to be displayed in Ulauncher
  * `aliases`: Aliases for the key (helps with Ulaunchers fuzzy searching)
  * `command`: Command to be run when the key is selected.

#### Example

##### Basic Config

```json
"lock": {
    "name": "Lock",
    "description": "Lock the session.",
    "icon": "system-lock-screen",
    "aliases": ["lock"],
    "command": "loginctl lock-session"
}
```

##### Disable Entry

```json
"lock": null
```

---

**Credits to [Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) for the current Icon of the extension**
