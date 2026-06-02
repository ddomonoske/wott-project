# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files

datas = []
datas += collect_data_files('customtkinter')
datas += collect_data_files('matplotlib')

hiddenimports = [
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends._backend_tk',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

if sys.platform == 'darwin':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='WOTT',
        debug=False,
        strip=False,
        upx=True,
        console=False,
        icon='media/WOTT_icon.icns',
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name='WOTT',
    )
    app = BUNDLE(
        coll,
        name='WOTT.app',
        icon='media/WOTT_icon.icns',
        bundle_identifier='com.wott.app',
        info_plist={
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'CFBundleShortVersionString': '1.0.0',
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='WOTT',
        debug=False,
        strip=False,
        upx=True,
        console=False,
        icon='media/WOTT_icon.ico' if sys.platform == 'win32' else None,
    )
