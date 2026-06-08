from collections.abc import Callable
import ctypes
import threading
import time


DEFAULT_HOTKEY = "ctrl+shift+space"

VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12
VK_SPACE = 0x20

POLL_INTERVAL_SECONDS = 0.03


class GlobalHotkeyManager:
    def __init__(self, callback: Callable[[], None], hotkey: str = DEFAULT_HOTKEY) -> None:
        self.callback = callback
        self.hotkey = hotkey
        self.is_registered = False
        self.is_hotkey_active = False
        self.stop_event = threading.Event()
        self.listener_thread: threading.Thread | None = None

    def register(self) -> None:
        if self.is_registered:
            return

        self.stop_event.clear()

        self.listener_thread = threading.Thread(
            target=self.listen_for_hotkey,
            daemon=True,
        )
        self.listener_thread.start()

        self.is_registered = True

    def unregister(self) -> None:
        if not self.is_registered:
            return

        self.stop_event.set()

        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=0.5)

        self.listener_thread = None
        self.is_hotkey_active = False
        self.is_registered = False

    def listen_for_hotkey(self) -> None:
        while not self.stop_event.is_set():
            hotkey_pressed = self.is_hotkey_pressed()

            if hotkey_pressed and not self.is_hotkey_active:
                self.is_hotkey_active = True
                self.callback()

            if not hotkey_pressed:
                self.is_hotkey_active = False

            time.sleep(POLL_INTERVAL_SECONDS)

    def is_hotkey_pressed(self) -> bool:
        if self.hotkey == "ctrl+shift+space":
            return (
                self.is_key_pressed(VK_CONTROL)
                and self.is_key_pressed(VK_SHIFT)
                and self.is_key_pressed(VK_SPACE)
            )

        if self.hotkey == "ctrl+alt+space":
            return (
                self.is_key_pressed(VK_CONTROL)
                and self.is_key_pressed(VK_MENU)
                and self.is_key_pressed(VK_SPACE)
            )

        return False

    def is_key_pressed(self, virtual_key_code: int) -> bool:
        return bool(ctypes.windll.user32.GetAsyncKeyState(virtual_key_code) & 0x8000)