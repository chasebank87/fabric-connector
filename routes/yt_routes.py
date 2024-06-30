from fastapi import APIRouter
import subprocess
import asyncio

yt_router = APIRouter()

@yt_router.get("/transcribe")
async def transcribe(url: str):
    """
    Runs the yt binary with the '--transcribe' option and returns the output.
    """
    try:
        output = await run_command(["yt", url])
        return {"transcription": output.decode().strip().split("\n")}
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