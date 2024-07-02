from builtins import WindowsError
import pystray
import threading
import os
import webbrowser
import logging
import sys
from PIL import Image
from api import start_api_server, stop_api_server
import winreg
import sys


# Set up logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fabric_yt_proxy.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

class FabricYTProxyApp:
    def __init__(self):
        logging.info("Initializing FabricYTProxyApp")
        self.icon = pystray.Icon("FabricYTProxy")
        self.api_thread = None
        self.setup_icon()
        self.start_api()

    def setup_icon(self):
        logging.info("Setting up icon")
        try:
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "fabric-brain.icns")
            image = Image.open(image_path)
            logging.info(f"Icon image loaded from {image_path}")
        except Exception as e:
            logging.error(f"Failed to load icon image: {e}")
            # Use a default icon or exit gracefully
            return

        menu = pystray.Menu(
            pystray.MenuItem("API Status", self.check_api_status),
            pystray.MenuItem("Start API", self.manual_start_api),
            pystray.MenuItem("Stop API", self.stop_api),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open API Docs", self.open_api_docs),
            pystray.MenuItem("Start at Login", self.toggle_start_at_login, checked=lambda item: self.is_start_at_login_enabled()),
            pystray.MenuItem("Exit", self.exit_app)
        )
        self.icon.icon = image
        self.icon.menu = menu

    def start_api(self):
        logging.info("Attempting to start API")
        if self.api_thread is None or not self.api_thread.is_alive():
            try:
                self.api_thread = threading.Thread(target=self.run_api_server, daemon=True)
                self.api_thread.start()
                logging.info("API thread started")
                self.icon.notify("API Started", "The API server is now running")
                self.update_menu_status(True)
            except Exception as e:
                logging.error(f"Failed to start API thread: {e}")
                self.icon.notify("Error", f"Failed to start API: {e}")
        else:
            logging.info("API already running")
            self.icon.notify("API Already Running", "The API server is already active")

    def run_api_server(self):
        try:
            logging.info("Running API server")
            start_api_server()
        except Exception as e:
            logging.error(f"Error in API server: {e}")
            self.icon.notify("API Error", f"API server encountered an error: {e}")

    def check_api_status(self):
        if self.api_thread and self.api_thread.is_alive():
            logging.info("API is running")
            self.icon.notify("API Status", "The API server is currently running")
        else:
            logging.info("API is not running")
            self.icon.notify("API Status", "The API server is not running")
            self.update_menu_status(False)

    def manual_start_api(self):
        logging.info("Manual API start requested")
        self.start_api()

    def stop_api(self):
        logging.info("Attempting to stop API")
        if self.api_thread and self.api_thread.is_alive():
            try:
                stop_api_server()
                self.api_thread.join(timeout=5)
                if not self.api_thread.is_alive():
                    self.api_thread = None
                    logging.info("API stopped successfully")
                    self.icon.notify("API Stopped", "The API server has been stopped")
                    self.update_menu_status(False)
                else:
                    logging.warning("Failed to stop API thread")
                    self.icon.notify("Error", "Failed to stop the API server")
            except Exception as e:
                logging.error(f"Error stopping API: {e}")
                self.icon.notify("Error", f"Error stopping API: {e}")
        else:
            logging.info("API not running, cannot stop")
            self.icon.notify("API Not Running", "The API server is not currently active")

    def open_api_docs(self):
        logging.info("Opening API docs")
        webbrowser.open('http://127.0.0.1:49152/docs')

    def exit_app(self):
        logging.info("Exiting application")
        self.stop_api()
        self.icon.stop()

    def update_menu_status(self, is_running):
        logging.info(f"Updating menu status: API {'running' if is_running else 'stopped'}")
        def create_menu(is_running):
            return pystray.Menu(
                pystray.MenuItem(f"API Status: {'Running' if is_running else 'Stopped'}", self.check_api_status),
                pystray.MenuItem("Start API", self.manual_start_api, enabled=not is_running),
                pystray.MenuItem("Stop API", self.stop_api, enabled=is_running),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Open API Docs", self.open_api_docs),
                pystray.MenuItem("Start at Login", self.toggle_start_at_login, checked=self.is_start_at_login_enabled()),
                pystray.MenuItem("Exit", self.exit_app)
            )
        self.icon.menu = create_menu(is_running)

    def is_start_at_login_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "FabricYTProxy")
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def toggle_start_at_login(self):
        if self.is_start_at_login_enabled():
            self.disable_start_at_login()
        else:
            self.enable_start_at_login()
        self.update_menu_status(self.api_thread and self.api_thread.is_alive())

    def enable_start_at_login(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "FabricYTProxy", 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
            logging.info("Start at login enabled")
            self.icon.notify("Start at Login", "Fabric YT Proxy will now start when you log in")
        except Exception as e:
            logging.error(f"Failed to enable start at login: {e}")
            self.icon.notify("Error", "Failed to enable start at login")

    def disable_start_at_login(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteValue(key, "FabricYTProxy")
            winreg.CloseKey(key)
            logging.info("Start at login disabled")
            self.icon.notify("Start at Login", "Fabric YT Proxy will no longer start when you log in")
        except Exception as e:
            logging.error(f"Failed to disable start at login: {e}")
            self.icon.notify("Error", "Failed to disable start at login")

    def run(self):
        logging.info("Running FabricYTProxyApp")
        self.icon.run()

def run():
    logging.info("Starting FabricYTProxyApp")
    try:
        FabricYTProxyApp().run()
    except Exception as e:
        logging.critical(f"Critical error in FabricYTProxyApp: {e}")
        raise