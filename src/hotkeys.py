from collections.abc import Callable

import keyboard


DEFAULT_HOTKEY = "ctrl+alt+space"


class GlobalHotkeyManager:
    def __init__(self, callback: Callable[[], None], hotkey: str = DEFAULT_HOTKEY) -> None:
        self.callback = callback
        self.hotkey = hotkey
        self.is_registered = False

    def register(self) -> None:
        if self.is_registered:
            return

        keyboard.add_hotkey(self.hotkey, self.callback)
        self.is_registered = True

    def unregister(self) -> None:
        if not self.is_registered:
            return

        keyboard.remove_hotkey(self.hotkey)
        self.is_registered = False