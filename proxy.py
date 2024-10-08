import subprocess
import os
import asyncio
import sys

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

def execute_fabric_command(command, path, goCompatible=False):
    try:
        if sys.platform == "darwin":
            result = subprocess.run([path, command], capture_output=True, text=True, check=True)
        elif sys.platform == "win32":
            if goCompatible:
                result = subprocess.run(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-WindowStyle", "Hidden", "-Command", path, command], capture_output=True, text=True, check=True)
            else:
                result = subprocess.run(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-WindowStyle", "Hidden", "-Command", "wsl -e", path, command], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        if goCompatible:
            if command == "--listpatterns":
                # Split the output into lines and create a list of pattern names
                patterns = [{"name": line.strip()} for line in output.split('\n') if line.strip()][1:]
                return patterns
        else:
            if command == "--list":
                # Split the output into lines and create a list of pattern names
                patterns = [{"name": line.strip()} for line in output.split('\n') if line.strip()]
                return patterns
            if command == "--listmodels":
                # Split the output into lines and create a list of pattern names
                models = [{"name": line.strip()} for line in output.split('\n') if line.strip()]
                return models
        
        return output
    except subprocess.CalledProcessError as e:
        return f"Error executing Fabric command: {e.stderr}"

def execute_yt_command(command):
    try:
        result = subprocess.run([YT_PATH, command], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing YT command: {e.stderr}"
    
async def run_command(command):
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    # Decode bytes to strings
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
    
    return stdout.strip()

def replace_drive(match):
    drive_letter = match.group(1).lower()  # Get the drive letter and convert to lowercase
    return f'/mnt/{drive_letter}/'

# Example usage
if __name__ == "__main__":
    print(execute_fabric_command("get-patterns"))
    print(execute_yt_command("example query"))