from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': 'assets/icons/fabric-logo-gif.icns',
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
        'cfIconFile': 'assets/icons/fabric-brain.icns',
        'CFBundleName': 'Fabric Connector',
    },
    'packages': ['rumps', 'fastapi', 'uvicorn', 'requests', 'multiprocessing', 'sys', 'threading', 'asyncio'],
}
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)