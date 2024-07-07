import os
from PyInstaller.utils.hooks import collect_submodules

# Manually set the project root
project_root = '/Users/armandpackham-mcguiness/Documents/Developer/JewelHarvest/Jewelharvest'

block_cipher = None

a = Analysis(
    ['Main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'Assets/Textures'), 'Assets/Textures'),
        (os.path.join(project_root, 'Assets/Other/icon.png'), 'Assets/Other'),
        (os.path.join(project_root, 'Assets/Other/Bitfantasy.ttf'), 'Assets/Other')
    ],
    hiddenimports=collect_submodules('pygame'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Jewelharvest',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Ensure console is disabled
    disable_windowed_traceback=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True  # Set to create a single file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Jewelharvest',
)