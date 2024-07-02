import rumps
import threading
import os
import webbrowser
import sys
import importlib
from Foundation import NSURL
from AppKit import NSWorkspace
from LaunchServices import (
    LSSharedFileListCreate,
    LSSharedFileListCopySnapshot,
    LSSharedFileListItemCopyResolvedURL,
    kLSSharedFileListSessionLoginItems,
    kLSSharedFileListItemLast,
    LSSharedFileListItemRemove,
    LSSharedFileListInsertItemURL
)
from api import start_api_server, stop_api_server



class FabricYTProxyApp(rumps.App):
    def __init__(self):
        super(FabricYTProxyApp, self).__init__("FabricYTProxy", icon=os.path.join("assets", "icons", "fabric-brain.icns"))
        self.menu = ["API Status", "Start API", "Stop API", None, "Open API Docs", "Start at Login"]
        self.api_thread = None
        self.start_api()
        self.login_item_exists = self.check_login_item()
        self.menu["Start at Login"].state = self.login_item_exists

    @rumps.clicked("Start at Login")
    def start_at_login(self, sender):
        sender.state = not sender.state
        self.toggle_login_item(sender.state)

    def toggle_login_item(self, state):
        if state:
            self.add_login_item()
        else:
            self.remove_login_item()

    def get_app_path(self):
        return NSWorkspace.sharedWorkspace().absolutePathForAppBundleWithIdentifier_(
            NSWorkspace.sharedWorkspace().frontmostApplication().bundleIdentifier()
        )

    def check_login_item(self):
        app_path = self.get_app_path()
        login_items = LSSharedFileListCreate(None, kLSSharedFileListSessionLoginItems, None)
        snapshot = LSSharedFileListCopySnapshot(login_items, None)[0]
        for item in snapshot:
            result = LSSharedFileListItemCopyResolvedURL(item, 0, None)
            if result is not None:
                item_url = result[0]
                if item_url is not None and item_url.path() == app_path:
                    return True
        return False

    def add_login_item(self):
        app_path = self.get_app_path()
        login_items = LSSharedFileListCreate(None, kLSSharedFileListSessionLoginItems, None)
        LSSharedFileListInsertItemURL(
            login_items,
            kLSSharedFileListItemLast,
            None,
            None,
            NSURL.fileURLWithPath_(app_path),
            {},
            None
        )

    def remove_login_item(self):
        app_path = self.get_app_path()
        login_items = LSSharedFileListCreate(None, kLSSharedFileListSessionLoginItems, None)
        snapshot = LSSharedFileListCopySnapshot(login_items, None)[0]
        for item in snapshot:
            result = LSSharedFileListItemCopyResolvedURL(item, 0, None)
            if result is not None:
                item_url = result[0]
                if item_url is not None and item_url.path() == app_path:
                    LSSharedFileListItemRemove(login_items, item)


    def start_api(self):
        if self.api_thread is None or not self.api_thread.is_alive():
            self.api_thread = threading.Thread(target=start_api_server, daemon=True)
            self.api_thread.start()
            rumps.notification("FabricYTProxy", "API Started", "The API server is now running")
            self.menu["API Status"].title = "API Status: Running"
            self.menu["Start API"].set_callback(None)
            self.menu["Stop API"].set_callback(self.stop_api)
        else:
            rumps.notification("FabricYTProxy", "API Already Running", "The API server is already active")

    @rumps.clicked("API Status")
    def check_api_status(self, _):
        if self.api_thread and self.api_thread.is_alive():
            rumps.notification("FabricYTProxy", "API Status", "The API server is currently running")
        else:
            rumps.notification("FabricYTProxy", "API Status", "The API server is not running")
            self.menu["API Status"].title = "API Status: Stopped"

    @rumps.clicked("Start API")
    def manual_start_api(self, _):
        self.start_api()

    @rumps.clicked("Stop API")
    def stop_api(self, _):
        if self.api_thread and self.api_thread.is_alive():
            stop_api_server()
            # Give the server a moment to start shutting down
            rumps.timer(2)
            self.api_thread.join(timeout=5)
            if not self.api_thread.is_alive():
                self.api_thread = None
                rumps.notification("FabricYTProxy", "API Stopped", "The API server has been stopped")
                self.menu["API Status"].title = "API Status: Stopped"
                self.menu["Start API"].set_callback(self.manual_start_api)
                self.menu["Stop API"].set_callback(None)
            else:
                rumps.notification("FabricYTProxy", "Error", "Failed to stop the API server")
        else:
            rumps.notification("FabricYTProxy", "API Not Running", "The API server is not currently active")

    @rumps.clicked("Open API Docs")
    def open_api_docs(self, _):
        webbrowser.open('http://127.0.0.1:49152/docs')

    def custom_import(name, *args, **kwargs):
        if name == 'imp':
            print(f"Attempted to import 'imp' from: {sys._getframe(1).f_code.co_filename}")
        return importlib.__import__(name, *args, **kwargs)

    sys.modules['builtins'].__import__ = custom_import

def run():
    FabricYTProxyApp().run()