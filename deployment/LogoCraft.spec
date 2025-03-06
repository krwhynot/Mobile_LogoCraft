# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Define runtime hooks - this is our custom hook to disable logging
runtime_hooks = [
    'disable_logging_hook.py'
]

# Define version information
VERSION = '1.0.0'
COMPANY_NAME = 'HungerRush'
PRODUCT_NAME = 'Mobile LogoCraft'
COPYRIGHT = '© 2025 HungerRush. All rights reserved.'
DESCRIPTION = 'Image processing tool for creating multiple sized app icons and graphics'

# Hard-code the paths to avoid __file__ issues
project_root = os.path.abspath('..')

# Define data files to include in the package - be minimal
datas = [
    # Include the main application icon
    (os.path.join(project_root, 'assets', 'icons', 'HungerRush_Icon.ico'), '.'),

    # Include only essential assets
    (os.path.join(project_root, 'assets', 'icons'), os.path.join('assets', 'icons')),
]

a = Analysis(
    [os.path.join(project_root, 'run.py')],  # Correct entry point
    pathex=[project_root],  # Add project root to the path
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PIL',
        'PIL._imaging',
        'cv2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,  # Add our custom runtime hook
    excludes=[
        'unittest', 'email', 'html', 'http', 'xml',
        'pydoc_data', 'distutils', 'tkinter', 'test',
        'lib2to3', 'matplotlib', 'scipy'
    ],  # Removed 'logging' from excludes
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Removed the loop that removes logging-related modules

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# This is the key part - we're building a single file
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # Include binaries
    a.zipfiles,       # Include zipfiles
    a.datas,          # Include data
    [],
    name=PRODUCT_NAME.replace(' ', '_'),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,         # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'icons', 'HungerRush_Icon.ico'),
    version='file_version_info.txt',
)
