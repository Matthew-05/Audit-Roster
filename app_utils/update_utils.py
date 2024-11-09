import requests
import zipfile
import shutil
import subprocess
import sys
import os
from packaging import version

def check_for_updates():
    try:
        # Replace with your GitHub repo API URL
        api_url = "https://api.github.com/repos/yourusername/your-repo/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(VERSION):
                return {
                    'update_available': True,
                    'version': latest_version,
                    'download_url': latest_release['assets'][0]['browser_download_url']
                }
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return {'update_available': False}

def download_and_install_update(download_url):
    try:
        # Create temp directory for update
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_update')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download update
        response = requests.get(download_url, stream=True)
        update_zip = os.path.join(temp_dir, 'update.zip')
        with open(update_zip, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        # Extract update
        with zipfile.ZipFile(update_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Create update script
        update_script = os.path.join(temp_dir, 'update.bat' if os.name == 'nt' else 'update.sh')
        script_content = '''
@echo off
timeout /t 2 /nobreak
xcopy /y /e "temp_update\*" "."
rmdir /s /q "temp_update"
start "" "{executable}"
        '''.format(executable=sys.executable) if os.name == 'nt' else '''
#!/bin/bash
sleep 2
cp -R temp_update/* .
rm -rf temp_update
{executable}
        '''.format(executable=sys.executable)
        
        with open(update_script, 'w') as f:
            f.write(script_content)
        
        # Execute update script and exit
        if os.name == 'nt':
            subprocess.Popen(['start', update_script], shell=True)
        else:
            os.chmod(update_script, 0o755)
            subprocess.Popen(['/bin/bash', update_script])
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error installing update: {e}")
        return False

