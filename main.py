import threading
import uvicorn
from fastapi import FastAPI
import rumps
import requests
import os
import signal
import time

from routes.fabric_routes import fabric_router
from routes.yt_routes import yt_router


app = FastAPI()
app.include_router(fabric_router)
app.include_router(yt_router)

class MyApp(rumps.App):
    def __init__(self):
        super(MyApp, self).__init__("My App", icon="assets/icons/fabric-brain.icns", quit_button=None)
        self.port = 49152
        self.menu.clear()
        self.api_docs_url = f"http://localhost:{self.port}/docs"
        self.menu = ["API Status", "Open API Docs"]

    @rumps.timer(5)
    def check_port(self, _):
        try:
            response = requests.get(self.api_docs_url)
            if response.status_code == 200:
                self.menu["API Status"].title = f"API Running on port {self.port}"
            else:
                self.menu["API Status"].title = f"API Error on port {self.port}"
        except requests.exceptions.RequestException:
            self.menu["API Status"].title = f"API Offline on port {self.port}"

    @rumps.clicked("Open API Docs")
    def open_api_docs(self, _):
        rumps.open_app(self.api_docs_url)
    
    @rumps.clicked("Quit")
    def quit_app(self, _):
        stop_event.set()
        rumps.quit_application()



def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=49152)

stop_event = threading.Event()

if __name__ == "__main__":
    # Start the FastAPI app in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()

    # Run the Rumps app in the main thread
    MyApp().run()