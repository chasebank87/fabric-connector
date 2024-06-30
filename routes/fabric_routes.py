from fastapi import APIRouter
import subprocess
import asyncio

fabric_router = APIRouter()

@fabric_router.get("/get-patterns")
async def get_patterns():
    """
    Runs the Fabric binary with the '--list' option and returns the output.
    """
    try:
        output = await run_command(["fabric", "--list"])
        return {"patterns": output.decode().strip().split("\n")}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}

@fabric_router.post("/run-fabric")
async def run_fabric(pattern: str, data: str):
    """
    Runs the Fabric binary with the provided command and returns the output.
    """
    try:
        output = await run_command(["fabric", "-sp", pattern, "--text", data])
        return {"output": output.decode().strip()}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}

async def run_command(command):
    """
    Runs a command asynchronously and returns the output.
    """
    process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
    return stdout