import pystray
import threading
import os
import webbrowser
from PIL import Image
from api import start_api_server, stop_api_server

class FabricYTProxyApp:
    def __init__(self):
        self.icon = pystray.Icon("FabricYTProxy")
        self.api_thread = None
        self.setup_icon()
        self.start_api()

    def setup_icon(self):
        image = Image.open(os.path.join("assets", "icons", "fabric-brain.png"))
        menu = pystray.Menu(
            pystray.MenuItem("API Status", self.check_api_status),
            pystray.MenuItem("Start API", self.manual_start_api),
            pystray.MenuItem("Stop API", self.stop_api),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open API Docs", self.open_api_docs),
            pystray.MenuItem("Exit", self.exit_app)
        )
        self.icon.icon = image
        self.icon.menu = menu

    def start_api(self):
        if self.api_thread is None or not self.api_thread.is_alive():
            self.api_thread = threading.Thread(target=start_api_server, daemon=True)
            self.api_thread.start()
            self.icon.notify("API Started", "The API server is now running")
            self.update_menu_status(True)
        else:
            self.icon.notify("API Already Running", "The API server is already active")

    def check_api_status(self):
        if self.api_thread and self.api_thread.is_alive():
            self.icon.notify("API Status", "The API server is currently running")
        else:
            self.icon.notify("API Status", "The API server is not running")
            self.update_menu_status(False)

    def manual_start_api(self):
        self.start_api()

    def stop_api(self):
        if self.api_thread and self.api_thread.is_alive():
            stop_api_server()
            self.api_thread.join(timeout=5)
            if not self.api_thread.is_alive():
                self.api_thread = None
                self.icon.notify("API Stopped", "The API server has been stopped")
                self.update_menu_status(False)
            else:
                self.icon.notify("Error", "Failed to stop the API server")
        else:
            self.icon.notify("API Not Running", "The API server is not currently active")

    def open_api_docs(self):
        webbrowser.open('http://127.0.0.1:49152/docs')

    def exit_app(self):
        self.stop_api()
        self.icon.stop()

    def update_menu_status(self, is_running):
        def create_menu(is_running):
            return pystray.Menu(
                pystray.MenuItem(f"API Status: {'Running' if is_running else 'Stopped'}", self.check_api_status),
                pystray.MenuItem("Start API", self.manual_start_api, enabled=not is_running),
                pystray.MenuItem("Stop API", self.stop_api, enabled=is_running),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Open API Docs", self.open_api_docs),
                pystray.MenuItem("Exit", self.exit_app)
            )
        self.icon.menu = create_menu(is_running)

    def run(self):
        self.icon.run()

def run():
    FabricYTProxyApp().run()