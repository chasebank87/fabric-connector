from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import subprocess
from typing import List, Dict
from proxy import execute_fabric_command, execute_yt_command, run_command
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
import shlex
import tempfile

# Set up logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fabric_yt_proxy_api.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "app://obsidian.md"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Command(BaseModel):
    command: str

class FabricRequest(BaseModel):
    pattern: str
    data: str

class YTRequest(BaseModel):
    pattern: str
    url: str

# Use os.path.expanduser to get the current user's home directory
if sys.platform == "darwin":
    HOME_DIR = os.path.expanduser("~")
    FABRIC_PATH = os.path.join(HOME_DIR, ".local", "bin", "fabric")
    YT_PATH = os.path.join(HOME_DIR, ".local", "bin", "yt")
elif sys.platform == "win32":
    HOME_DIR = os.path.expanduser("~").replace("Users", "home").replace("C:", "")
    FABRIC_PATH = os.path.join(HOME_DIR, ".local", "bin", "fabric").replace("\\", "/")
    YT_PATH = os.path.join(HOME_DIR, ".local", "bin", "yt").replace("\\", "/")
else:
    print("Unsupported operating system")
    sys.exit(1)


@app.post("/fabric")
async def fabric(request: FabricRequest):
    """
    Runs the Fabric binary with the provided command and returns the output.
    """
    try:
        logging.info(f"Running Fabric command with pattern: {request.pattern}")
        if sys.platform == "darwin":
            output = await run_command([FABRIC_PATH, "-sp", request.pattern, "--text", request.data])
        elif sys.platform == "win32":
            if request.data:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(request.data)
                    temp_file_path = temp_file.name
            powershell_command = f"gc '{temp_file_path}' | wsl -e {FABRIC_PATH} -sp '{request.pattern}'"
            output = await run_command(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", powershell_command])
            os.unlink(temp_file_path)
        logging.info("Fabric command executed successfully")
        return {"output": output}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing Fabric command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/yt")
async def yt(request: YTRequest):
    """
    Runs the yt binary with the provided command and returns the output.
    """
    try:
        logging.info(f"Running YT command with URL: {request.url}")
        if sys.platform == "darwin":
            transcript = await run_command([YT_PATH, request.url])
            output = await run_command([FABRIC_PATH, "-sp", request.pattern, "--text", transcript])
        elif sys.platform == "win32":
            output = await run_command(["wsl", "-e", YT_PATH, request.url])
            if output:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(output)
                    temp_file_path = temp_file.name
                powershell_command = f"gc '{temp_file_path}' | wsl -e {FABRIC_PATH} -sp '{request.pattern}'"
                output = await run_command(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", powershell_command])
                os.unlink(temp_file_path)
        logging.info("YT command executed successfully, running Fabric command")
        logging.info("Fabric command executed successfully")
        return {"output": output}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing YT or Fabric command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patterns")
async def get_patterns():
    logging.info("Retrieving patterns")
    if sys.platform == "darwin":
        result = execute_fabric_command("--list")
    elif sys.platform == "win32":
        result = execute_fabric_command("--list")
    if isinstance(result, list):
        logging.info("Patterns retrieved successfully")
        return {"data": {"patterns": result}}
    else:
        logging.error(f"Error retrieving patterns: {str(result)}")
        raise HTTPException(status_code=500, detail=str(result))

server = None

def start_api_server():
    global server
    logging.info("Starting API server")
    config = uvicorn.Config(app, host="127.0.0.1", port=49152, loop="asyncio", log_config=None)
    server = uvicorn.Server(config)
    try:
        server.run()
    except Exception as e:
        logging.error(f"Error starting API server: {str(e)}")
        raise

def stop_api_server():
    global server
    if server:
        logging.info("Stopping API server")
        server.should_exit = True
    else:
        logging.warning("Attempted to stop API server, but it was not running")

def sanitize_for_shell(input_string):
    return shlex.quote(input_string)

if __name__ == "__main__":
    start_api_server()