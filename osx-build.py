
import subprocess
import site
import os
import shutil


app_name = 'Tiled ZoeDepth GUI' 

# # Step 1: Remove old build/dist
# subprocess.run(['rm', '-rf', 'build', 'dist'])
# # Step 2: build .app
# subprocess.run(['python', 'setup.py', 'py2app'])

# # Step 3: Copy torch folder from site-packages and replace torch version inside .app
# site_packages = site.getsitepackages()[0]
# python_version = f"{site_packages.split('/')[-2]}"
# app_path = f"dist/{app_name}.app/Contents/Resources/lib/{python_version}"

# torch_site_path = os.path.join(site_packages, 'torch')
# torch_app_path = os.path.join(app_path, 'torch')

# if os.path.exists(torch_app_path):
#     shutil.rmtree(torch_app_path)

# shutil.copytree(torch_site_path, torch_app_path)

#Step 5: Create DMG
if os.path.exists(f'./{app_name}.dmg'):
    os.remove(f'{app_name}.dmg')

subprocess.run(['dmgbuild', '-s', 'dmgbuild.py', '-D', 'filesystem="APFS"', app_name, f'{app_name}.dmg'])

print('Build Done!')