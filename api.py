from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
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
import shutil
import hashlib
import uuid

# Set up logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fabric_yt_proxy_api.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_hardware_uuid():
    if sys.platform == "darwin":
        result = subprocess.run(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if "IOPlatformUUID" in line:
                return line.split('=')[1].strip().strip('"')
    elif sys.platform == "win32":
        result = subprocess.run(["wmic", "csproduct", "get", "UUID"], capture_output=True, text=True)
        return result.stdout.split('\n')[1].strip()
    else:
        raise Exception("Unsupported platform")

def generate_api_key():
    hardware_uuid = get_hardware_uuid()
    key = hashlib.sha256(hardware_uuid.encode()).hexdigest()
    return key

API_KEY = generate_api_key()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

app = FastAPI(dependencies=[Depends(get_api_key)])

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

class Model(BaseModel):
    model: str

class UpdatePatternRequest(BaseModel):
    pattern: str
    content: str

class DeletePatternRequest(BaseModel):
    pattern: str

class FabricRequest(BaseModel):
    pattern: list[str]
    model: str
    data: str
    stream: bool

class YTRequest(BaseModel):
    pattern: list[str]
    model: str
    url: str
    stream: bool

class TSRequest(BaseModel):
    pattern: list[str]
    model: str
    path: str
    stream: bool

# Use os.path.expanduser to get the current user's home directory
if sys.platform == "darwin":
    HOME_DIR = os.path.expanduser("~")
    FABRIC_PATH = os.path.join(HOME_DIR, ".local", "bin", "fabric")
    YT_PATH = os.path.join(HOME_DIR, ".local", "bin", "yt")
    TS_PATH = os.path.join(HOME_DIR, ".local", "bin", "ts")
    PATTERN_PATH = os.path.join(HOME_DIR, ".config", "fabric", "patterns")
elif sys.platform == "win32":
    HOME_DIR = os.path.expanduser("~").replace("Users", "home").replace("C:", "")
    FABRIC_PATH = os.path.join(HOME_DIR, ".local", "bin", "fabric").replace("\\", "/")
    YT_PATH = os.path.join(HOME_DIR, ".local", "bin", "yt").replace("\\", "/")
    TS_PATH = os.path.join(HOME_DIR, ".local", "bin", "ts").replace("\\", "/")
    PATTERN_PATH = os.path.join(HOME_DIR, ".config", "fabric", "patterns").replace("\\", "/")
else:
    print("Unsupported operating system")
    sys.exit(1)

@app.post("/fabric")
async def fabric(request: FabricRequest):
    """
    Runs the Fabric binary with the provided command and returns the output.
    """
    try:
        logging.info(f"Running Fabric command with patterns: {request.pattern}")
        final_output = ""
        input_data = request.data
        
        for pattern in request.pattern:
            if sys.platform == "darwin":
                output = await run_command([FABRIC_PATH, "-sp", pattern, "--text", input_data, "--model", request.model])
            elif sys.platform == "win32":
                if input_data:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                        temp_file.write(input_data)
                        temp_file_path = temp_file.name
                powershell_command = f"gc '{temp_file_path}' | wsl -e {FABRIC_PATH} -sp '{pattern}' --model '{request.model}'"
                output = await run_command(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", powershell_command])
                os.unlink(temp_file_path)
            
            if request.stream:
                input_data = output  # Use the output of the current pattern as the input for the next
                final_output = output  # The final output is the last pattern's output
            else:
                final_output += output + "\n\n"  # Concatenate outputs if not streaming
        
        logging.info("Fabric command executed successfully")
        return {"output": final_output.strip()}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing Fabric command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_models():
    logging.info("Retrieving models")
    if sys.platform in ["darwin", "win32"]:
        result = execute_fabric_command("--listmodels")
    else:
        logging.error(f"Unsupported platform: {sys.platform}")
        raise HTTPException(status_code=500, detail="Unsupported platform")

    if isinstance(result, list):
        filtered_models = [
            {"name": item['name']} for item in result 
            if 'name' in item and item['name'] not in [
                'GPT Models:', 'Local Models:', 'Claude Models:', 'Google Models:'
            ] and item['name'].strip()
        ]
        
        logging.info(f"Models retrieved successfully. Count: {len(filtered_models)}")
        return {
            "data": {
                "models": filtered_models
            }
        }
    else:
        logging.error(f"Unexpected result type: {type(result)}. Content: {str(result)}")
        raise HTTPException(status_code=500, detail="Unexpected result format from execute_fabric_command")



@app.post("/set_model")
async def set_model(request: Model):
    """
    Sets the model to be used by the Fabric binary.
    """
    try:
        logging.info(f"Setting model to: {request.model}")
        if sys.platform == "darwin":
            output = await run_command([FABRIC_PATH, "--changeDefaultModel", request.model])
        elif sys.platform == "win32":
            powershell_command = f"wsl -e {FABRIC_PATH} --changeDefaultModel '{request.model}'"
            output = await run_command(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", powershell_command])
        logging.info("Model set successfully")
        return {"output": output}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting model: {str(e)}")
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
        elif sys.platform == "win32":
            transcript = await run_command(["wsl", "-e", YT_PATH, request.url])
        
        logging.info("YT command executed successfully, running Fabric command")
        
        final_output = ""
        input_data = transcript
        
        for pattern in request.pattern:
            if sys.platform == "darwin":
                output = await run_command([FABRIC_PATH, "-sp", pattern, "--text", input_data, "--model", request.model])
            elif sys.platform == "win32":
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(input_data)
                    temp_file_path = temp_file.name
                powershell_command = f"gc '{temp_file_path}' | wsl -e {FABRIC_PATH} -sp '{pattern}' --model {request.model}"
                output = await run_command(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", powershell_command])
                os.unlink(temp_file_path)
            
            if request.stream:
                input_data = output  # Use the output of the current pattern as the input for the next
                final_output = output  # The final output is the last pattern's output
            else:
                final_output += output + "\n\n"  # Concatenate outputs if not streaming
        
        logging.info("Fabric command executed successfully")
        return {"output": final_output.strip()}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing YT or Fabric command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ts")
async def ts(request: TSRequest):
    """
    Runs the ts binary with the provided command and returns the output.
    """
    try:
        logging.info(f"Running TS command with file: {request.path}")
        if sys.platform == "darwin":
            transcript = await run_command([TS_PATH, request.path])
        elif sys.platform == "win32":
            transcript = await run_command(["wsl", "-e", YT_PATH, request.path])
        
        logging.info("YT command executed successfully, running Fabric command")
        
        final_output = ""
        input_data = transcript
        
        for pattern in request.pattern:
            if sys.platform == "darwin":
                output = await run_command([FABRIC_PATH, "-sp", pattern, "--text", input_data, "--model", request.model])
            elif sys.platform == "win32":
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(input_data)
                    temp_file_path = temp_file.name
                powershell_command = f"gc '{temp_file_path}' | wsl -e {FABRIC_PATH} -sp '{pattern}' --model {request.model}"
                output = await run_command(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", powershell_command])
                os.unlink(temp_file_path)
            
            if request.stream:
                input_data = output  # Use the output of the current pattern as the input for the next
                final_output = output  # The final output is the last pattern's output
            else:
                final_output += output + "\n\n"  # Concatenate outputs if not streaming
        
        logging.info("Fabric command executed successfully")
        return {"output": final_output.strip()}
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

@app.post("/update_pattern")
async def update_pattern(request: UpdatePatternRequest):
    """
    Updates pattern contents or creates new patterns
    """
    try:
        # Construct the full path for the pattern file
        pattern_file_path = os.path.join(PATTERN_PATH, request.pattern, 'system.md')
        
        # Check if the file already exists
        file_existed = os.path.exists(pattern_file_path)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(pattern_file_path), exist_ok=True)

        # Write the content to the file
        with open(pattern_file_path, 'w') as f:
            f.write(request.content)

        if file_existed:
            logging.info(f"Pattern '{request.pattern}' updated successfully")
            return {"message": f"Pattern '{request.pattern}' updated successfully"}
        else:
            logging.info(f"Pattern '{request.pattern}' created successfully")
            return {"message": f"Pattern '{request.pattern}' created successfully"}

    except IOError as e:
        logging.error(f"Error writing pattern file: {e}")
        raise HTTPException(status_code=500, detail=f"Error writing pattern file: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/delete_pattern")
async def delete_pattern(request: DeletePatternRequest):
    """
    Deletes a pattern folder from the Fabric patterns directory
    """
    try:
        pattern_folder_path = os.path.join(PATTERN_PATH, request.pattern)
        
        if os.path.exists(pattern_folder_path):
            if os.path.isdir(pattern_folder_path):
                shutil.rmtree(pattern_folder_path)
                logging.info(f"Pattern folder '{request.pattern}' deleted successfully")
                return {"message": f"Pattern folder '{request.pattern}' deleted successfully"}
            else:
                os.remove(pattern_folder_path)
                logging.info(f"Pattern file '{request.pattern}' deleted successfully")
                return {"message": f"Pattern file '{request.pattern}' deleted successfully"}
        else:
            logging.warning(f"Pattern '{request.pattern}' not found")
            return {"message": f"Pattern '{request.pattern}' not found"}

    except PermissionError as e:
        logging.error(f"Permission error deleting pattern: {e}")
        raise HTTPException(status_code=403, detail=f"Permission error deleting pattern: {str(e)}")
    except IOError as e:
        logging.error(f"Error deleting pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting pattern: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

server = None

def start_api_server():
    global server
    logging.info("Starting API server")
    config = uvicorn.Config(app, host="0.0.0.0", port=49152, loop="asyncio", log_config=None)
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