from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import subprocess
from typing import List, Dict
from proxy import execute_fabric_command, execute_yt_command, run_command
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", 'app://obsidian.md'],
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

FABRIC_PATH = "/Users/chase/.local/bin/fabric"
YT_PATH = "/Users/chase/.local/bin/yt"


@app.post("/fabric")
async def fabric(request: FabricRequest):
    """
    Runs the Fabric binary with the provided command and returns the output.
    """
    try:
        output = await run_command([FABRIC_PATH, "-sp", request.pattern, "--text", request.data])
        return {"output": output.decode().strip()}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/yt")
async def yt(request: YTRequest):
    """
    Runs the yt binary with the provided command and returns the output.
    """
    try:
        transcript = await run_command([YT_PATH, request.url])
        output = await run_command([FABRIC_PATH, "-sp", request.pattern, "--text", transcript])
        return {"output": output.decode().strip()}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patterns")
async def get_patterns():
    result = execute_fabric_command("--list")
    if isinstance(result, list):
        return {"data": {"patterns": result}}
    else:
        raise HTTPException(status_code=500, detail=str(result))

server = None

def start_api_server():
    global server
    config = uvicorn.Config(app, host="127.0.0.1", port=49152, loop="asyncio")
    server = uvicorn.Server(config)
    server.run()

def stop_api_server():
    global server
    if server:
        server.should_exit = True

if __name__ == "__main__":
    start_api_server()