# -*- mode: python ; coding: utf-8 -*-


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
        ('/opt/homebrew/anaconda3/envs/fabric_yt_proxy/bin/Info.plist', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Fabric Connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/fabric-logo-gif.icns',
    onefile=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Fabric Connector',
)

# For macOS, add the following to create a .app bundle
app = BUNDLE(
    coll,
    name='Fabric Connector.app',
    icon='assets/icons/fabric-logo-gif.icns',
    bundle_identifier='com.chaseelder.fabric_connector',
)