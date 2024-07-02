# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Define the path for log files
log_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'logs')
os.makedirs(log_dir, exist_ok=True)
stdout_log = os.path.join(log_dir, 'stdout.log')
stderr_log = os.path.join(log_dir, 'stderr.log')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('api.py', '.'),
        ('macos_app.py', '.'),
        ('proxy.py', '.'),
        ('windows_app.py', '.'),
        ('assets/icons/fabric-logo-gif.icns', 'assets/icons/'),
        ('assets/icons/fabric-brain.icns', 'assets/icons/'),
        ('Info.plist', '.'),
    ],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Fabric Connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/fabric-logo-gif.icns',
    onefile=True,
    stdout=stdout_log,
    stderr=stderr_log,
)

# For macOS, add the following to create a .app bundle
app = BUNDLE(
    exe,
    name='Fabric Connector.app',
    icon='assets/icons/fabric-logo-gif.icns',
    bundle_identifier='com.chaseelder.fabric_connector',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'My File Format',
                'CFBundleTypeIconFile': 'assets/icons/fabric-logo-gif.icns',
                'LSItemContentTypes': ['com.example.myformat'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)