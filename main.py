import sys
import os
from macos_app import run

if sys.platform == "darwin":
    from macos_app import run
elif sys.platform == "win32":
    from windows_app import run
else:
    print("Unsupported operating system")
    sys.exit(1)

if __name__ == "__main__":
    run()