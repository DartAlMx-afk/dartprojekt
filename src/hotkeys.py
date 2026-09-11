import keyboard
import pyperclip
import time
import threading
from .logger import logger
from .ai_client import ai_client
from .config import config_manager
from .notifier import Notifier

class HotkeyManager:
    def __init__(self, status_callback=None):
        self.is_running = False
        self.status_callback = status_callback
        self.is_processing = False # Debounce flag to prevent double-triggers

    def _hotkey_thread(self):
        # Debounce mechanism: if we are already processing a hotkey press, ignore subsequent ones.
        if self.is_processing:
            logger.debug("Hotkey triggered while already processing. Ignoring (debounce).")
            return

        self.is_processing = True

        try:
            hotkey_used = config_manager.get("hotkey")
            logger.info(f"Hotkey '{hotkey_used}' pressed! Starting correction process...")

            try:
                original_clipboard = pyperclip.paste()
            except Exception as e:
                logger.error(f"Failed to access original clipboard: {e}")
                original_clipboard = ""

            pyperclip.copy("")

            last_key = hotkey_used.split("+")[-1].strip().lower()

            logger.debug(f"Releasing modifier keys and trigger key '{last_key}'...")
            keyboard.release("ctrl")
            keyboard.release("shift")
            keyboard.release("alt")
            keyboard.release("win")
            keyboard.release("right ctrl")
            keyboard.release("right shift")
            keyboard.release("right alt")
            try:
                keyboard.release(last_key)
            except Exception:
                pass

            time.sleep(0.1)

            copy_delay = float(config_manager.get("copy_delay"))
            paste_delay = float(config_manager.get("paste_delay"))

            logger.debug(f"Sending 'ctrl+insert' and waiting {copy_delay}s...")
            keyboard.send("ctrl+insert")
            time.sleep(copy_delay)

            try:
                selected_text = pyperclip.paste()
            except Exception as e:
                logger.error(f"Failed to read clipboard after copy: {e}")
                selected_text = ""

            if not selected_text or selected_text.isspace():
                logger.warning("No text selected or failed to copy. Restoring clipboard.")
                pyperclip.copy(original_clipboard)
                Notifier.show_error()
                return

            logger.info(f"Successfully copied text: {len(selected_text)} chars.")

            fixed_text = ai_client.fix_text(selected_text)

            if fixed_text:
                logger.info("Successfully received corrected text. Ready to paste.")
                try:
                    pyperclip.copy(fixed_text)
                    time.sleep(paste_delay)
                    logger.debug(f"Sending 'shift+insert'...")
                    keyboard.send("shift+insert")
                    time.sleep(0.1)
                    Notifier.show_success()
                except Exception as e:
                    logger.error(f"Failed to paste corrected text: {e}")
                    Notifier.show_error()
            else:
                logger.warning("Failed to get corrected text from AI. Restoring clipboard.")
                try:
                    pyperclip.copy(original_clipboard)
                except Exception as e:
                    logger.error(f"Failed to restore original clipboard: {e}")
                Notifier.show_error()

        except Exception as general_error:
            logger.error(f"Unexpected error in hotkey thread: {general_error}")
            Notifier.show_error()
        finally:
            # Ensure the lock is released even if an error occurs
            self.is_processing = False

    def on_hotkey(self):
        threading.Thread(target=self._hotkey_thread, daemon=True).start()

    def start_tracking(self):
        if not self.is_running:
            hotkey = config_manager.get("hotkey")
            try:
                keyboard.add_hotkey(hotkey, self.on_hotkey)
                self.is_running = True
                logger.info(f"Started hotkey tracking ({hotkey}).")
                if self.status_callback:
                    self.status_callback(True)
            except Exception as e:
                logger.error(f"Failed to bind hotkey '{hotkey}': {e}")

    def stop_tracking(self):
        if self.is_running:
            try:
                keyboard.remove_all_hotkeys()
            except Exception as e:
                logger.error(f"Error removing hotkeys: {e}")
            self.is_running = False
            logger.info("Stopped hotkey tracking.")
            if self.status_callback:
                self.status_callback(False)

    def toggle_tracking(self):
        if self.is_running:
            self.stop_tracking()
        else:
            self.start_tracking()

hotkey_manager = HotkeyManager()
