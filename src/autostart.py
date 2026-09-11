import os
import sys
from .logger import logger

def setup_autostart(enable: bool):
    try:
        import winreg
    except ImportError:
        logger.warning("winreg not available, autostart only supported on Windows.")
        return

    try:
        # Path to the current executable or script
        if getattr(sys, 'frozen', False):
            # If bundled by PyInstaller
            app_path = sys.executable
        else:
            # If running as script, use pythonw and the run script
            # Assuming we want to run run_hidden.vbs to avoid console window
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            vbs_path = os.path.join(base_dir, 'run_hidden.vbs')
            if os.path.exists(vbs_path):
                 app_path = f'wscript.exe "{vbs_path}"'
            else:
                 # Fallback to pythonw if vbs is missing
                 python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
                 script_path = os.path.join(base_dir, 'src', 'main.py')
                 app_path = f'"{python_exe}" "{script_path}"'

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "AITextCorrector"

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)

        if enable:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            logger.info(f"Autostart enabled. Path: {app_path}")
        else:
            try:
                winreg.DeleteValue(key, app_name)
                logger.info("Autostart disabled.")
            except FileNotFoundError:
                pass # Already disabled

        winreg.CloseKey(key)

    except Exception as e:
        logger.error(f"Error configuring autostart: {e}")
