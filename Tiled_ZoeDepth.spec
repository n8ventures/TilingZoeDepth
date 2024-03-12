# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
site_packages='.conda\\Lib\\site-packages\\'

datas = [ 
    ('ZoeDepth2.ico', '.'),
    (f'{site_packages}tkinterdnd2', 'tkinterdnd2'),
]
datas += collect_data_files('pyinstaller_hooks_contrib.collect')

modules_to_include = [
    'numpy',
    'torchvision',
    'torchaudio',
    'matplotlib',
    'scipy',
    'os',
    'gitdb',
    'timm'
]

a = Analysis( # type: ignore
    ['Tiled_ZoeDepth.py'],
    pathex=['.conda\\Lib\\site-packages'],
    binaries=[],
    datas=datas,
    hiddenimports=modules_to_include,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure) # type: ignore

exe = EXE( # type: ignore
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Tiled_ZoeDepth',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["ZoeDepth2.ico"],
    version='Version.rc'
)
coll = COLLECT( # type: ignore
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Tiled_ZoeDepth',
)
