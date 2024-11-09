import requests
import zipfile
import shutil
import subprocess
import sys
import os
from packaging import version

def check_for_updates(VERSION):
    try:
        # Replace with your GitHub repo API URL
        api_url = "https://api.github.com/repos/Matthew-05/Audit-Roster/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            
            # Check if there are any assets before trying to access them
            if latest_release['zipball_url']:
                download_url = latest_release['zipball_url']
            else:
                print("No assets found in the release")
                return {'update_available': False}
            
            if version.parse(latest_version) > version.parse(VERSION):
                return {
                    'update_available': True,
                    'version': latest_version,
                    'download_url': download_url
                }
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return {'update_available': False}

def download_and_install_update(download_url):
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create progress window
        root = tk.Tk()
        root.title("Updating Staff Scheduler")
        root.geometry("300x150")
        root.attributes('-topmost', True)
        
        # Center the window
        root.eval('tk::PlaceWindow . center')
        
        label = ttk.Label(root, text="Installing update...", padding=20)
        label.pack()
        
        progress = ttk.Progressbar(root, mode='indeterminate', length=200)
        progress.pack(pady=20)
        progress.start()
        
        # Create temp directory for update
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_dir = os.path.join(base_dir, 'temp_update')
        os.makedirs(temp_dir, exist_ok=True)
        
        def perform_update():
            # Download update
            response = requests.get(download_url, stream=True)
            update_zip = os.path.join(temp_dir, 'update.zip')
            with open(update_zip, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            # Extract update
            with zipfile.ZipFile(update_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Find the extracted directory
            extracted_dir = None
            for item in os.listdir(temp_dir):
                if item.startswith('Matthew-05-Audit-Roster'):
                    extracted_dir = os.path.join(temp_dir, item)
                    break
            
            if not extracted_dir:
                raise Exception("Could not find extracted update directory")
            
            # Create and execute update script silently
            batch_file = os.path.join(temp_dir, 'update.bat')
            script_content = f'''
@echo off
cd /d "{base_dir}"
robocopy "{extracted_dir}" "{base_dir}" /E /IS /IT /IM /NFL /NDL /NJH /NJS
rd /s /q "{temp_dir}" 2>nul
start "" "{sys.executable}"
'''
            with open(batch_file, 'w') as f:
                f.write(script_content)
            
            os.system(f'cmd /c "{batch_file}" >nul 2>&1')
            root.destroy()
            sys.exit(0)
            
        root.after(500, perform_update)
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"Error installing update: {e}")
        return False

