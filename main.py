import sys
import os

if sys.platform == "darwin":
    os.environ["PATH"] = os.pathsep.join(("/opt/homebrew/bin", "/opt/homebrew/anaconda3/bin/", os.environ["PATH"]))
    from macos_app import run
elif sys.platform == "win32":
    from windows_app import run
else:
    print("Unsupported operating system")
    sys.exit(1)

if __name__ == "__main__":
    run()