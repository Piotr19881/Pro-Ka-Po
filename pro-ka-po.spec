# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file dla Pro-Ka-Po
Użycie: pyinstaller pro-ka-po.spec
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Ścieżki
project_dir = os.path.abspath('.')
src_dir = os.path.join(project_dir, 'src')

# Dane do dołączenia
datas = []

# Ukryte importy (używane dynamicznie)
hiddenimports = [
    'keyboard',
    'python_dateutil',
]

# Lista modułów do wykluczenia (oszczędność ~80-100 MB)
excludes = [
    # PyQt6 - nieużywane moduły
    'PyQt6.QtWebEngine',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.Qt3DAnimation',
    'PyQt6.Qt3DCore',
    'PyQt6.Qt3DExtras',
    'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic',
    'PyQt6.Qt3DRender',
    'PyQt6.QtBluetooth',
    'PyQt6.QtNfc',
    'PyQt6.QtPositioning',
    'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    'PyQt6.QtSql',
    'PyQt6.QtTest',
    'PyQt6.QtXml',
    'PyQt6.QtNetworkAuth',
    'PyQt6.QtWebSockets',
    'PyQt6.QtCharts',
    'PyQt6.QtDataVisualization',
    'PyQt6.QtQuick',
    'PyQt6.QtQuick3D',
    'PyQt6.QtQuickControls2',
    'PyQt6.QtQuickWidgets',
    'PyQt6.QtRemoteObjects',
    'PyQt6.QtScxml',
    'PyQt6.QtStateMachine',
    'PyQt6.QtSvg',
    'PyQt6.QtSvgWidgets',
    'PyQt6.QtVirtualKeyboard',
    'PyQt6.QtWebChannel',
    # Python stdlib - nieużywane
    'tkinter',
    'test',
    'unittest',
    'pydoc_data',
    'doctest',
    'xmlrpc',
    'lib2to3',
    # Inne
    'PIL',
    'numpy',
    'pandas',
    'matplotlib',
    'scipy',
]

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Pro-Ka-Po',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Kompresja UPX (opcjonalnie, wymaga UPX)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Bez okna konsoli
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,  # Opcjonalnie: dodaj ikonę
)
