from setuptools import setup
import site
import glob
import os
from __version__ import appver as __version__
import sys
import py2app.recipes
sys.setrecursionlimit(10000)


icon = 'ZoeDepth2.icns'
app_name='Tiled ZoeDepth GUI'

site_packages = site.getsitepackages()[0]
python_version = f"{site_packages.split('/')[-2]}"

class ExcludeFromZip_Recipe(object):
    def __init__(self, module):
        self.module = module

    def check(self, cmd, mf):
        m = mf.findNode(self.module)
        if m is None:
            return None

        # Don't put the module in the site-packages.zip file
        return {"packages": [self.module]}

APP = ['Tiled_ZoeDepth-OSX.py']
OPTIONS = {
    'iconfile': icon, 
    'packages':[
        'filelock',
        'tk',
        'tkinter',
        'tkinterdnd2',
        'subprocess', 
        'tkmacosx',
        'fsspec',
        'markupsafe',
        'matplotlib',
        'mpmath',
        'networkx',
        'numpy',
        'jinja2',
        'sympy',
        'cv2',
        'PIL',
        'timm',
        'tomlkit',
        'toolz',
        'tqdm',
        ],
    'includes':[
        'requests',
        'subprocess',
        'sys',
        'atexit',
        'tkinter',
        'os',
        'json',
        'shutil',
        'threading',
        'time',
        'math',
        'glob',
        'platform',
        ],
    'excludes':[
        'ZoeDepth',
                ],
    'frameworks':[
        '/opt/homebrew/Cellar/tcl-tk/8.6.14/lib/libtk8.6.dylib',
        '/opt/homebrew/Cellar/tcl-tk/8.6.14/lib/libtcl8.6.dylib',
    ],
    'plist': {
        'NSHumanReadableCopyright': 
            'Copyright © 2022 Intelligent Systems Lab Org. Copyright © 2024 BillFSmith. Copyright © 2024 John Nathaniel Calvara. This software is licensed under the MIT License.',
        'CFBundleIdentifier':
            "dev.n8ventures.N8TiledZoeDepthGUI",
        'NSAppleScriptEnabled':
            True,
        'CFBundleGetInfoString':
            'Create Depth maps using ZoeDepth by Intel Labs. Tiling Modification by BillFSmith.',
        }
}

DATA_FILES=[   
    ('.', [
        'ZoeDepth2.icns',
        './assets/ZoeDepth2.png',
        ]),
     ('../lib', ['/opt/homebrew/Cellar/tcl-tk/8.6.14/lib/']),
        ]

# DATA_FILES += [(f'lib/{python_version}/torch/lib', torch_libs)]


for module in [
    'torch', 'torchvision', 'torchaudio', 'torchgen'
    ]:
    setattr( py2app.recipes, module, ExcludeFromZip_Recipe(module) )

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name=app_name,
    version= __version__,
    description='Create Depth maps using ZoeDepth by Intel Labs. Tiling Modification by BillFSmith.',
    author='John Nathaniel Calvara, Intel Labs, BillFSmith',
    author_email='nate@n8ventures.dev',
    url='https://github.com/n8ventures/TilingZoeDepth_GUI',
)
