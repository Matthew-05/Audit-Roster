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
            exe_asset = None
            internal_zip_asset = None
            for asset in latest_release['assets']:
                if asset['name'].endswith('.exe') and 'installer' not in asset['name'].lower():
                    exe_asset = asset
                elif asset['name'].endswith('.zip'):
                    internal_zip_asset = asset
            
            if exe_asset and internal_zip_asset:
                exe_download_url = exe_asset['browser_download_url']
                internal_zip_download_url = internal_zip_asset['browser_download_url']
                print(f"Executable Download URL: {exe_download_url}")
                print(f"Internal ZIP Download URL: {internal_zip_download_url}")
            else:
                print("Required assets not found in the release")
                return {'update_available': False}
            
            if version.parse(latest_version) > version.parse(VERSION):
                return {
                    'update_available': True,
                    'version': latest_version,
                    'exe_download_url': exe_download_url,
                    'internal_zip_download_url': internal_zip_download_url
                }
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return {'update_available': False}

def download_and_install_update(download_url, internal_zip_url):
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        
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
            # Prompt user to backup the database
            backup_db = messagebox.askyesno("Backup Database", "Do you want to backup the database before updating?")
            
            if backup_db:
                # Backup the database
                db_path = os.path.join(base_dir, 'employee_scheduler.db')
                backup_path = os.path.join(base_dir, 'employee_scheduler_backup.db')
                shutil.copyfile(db_path, backup_path)
            
            # Download the executable
            exe_path = os.path.join(temp_dir, 'staff_scheduler.exe')
            response = requests.get(download_url)
            with open(exe_path, 'wb') as f:
                f.write(response.content)
            
            # Download the internal ZIP file
            internal_zip_path = os.path.join(temp_dir, 'internal.zip')
            response = requests.get(internal_zip_url)
            with open(internal_zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract the internal ZIP file
            with zipfile.ZipFile(internal_zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Create and execute update script silently
            batch_file = os.path.join(temp_dir, 'update.bat')
            script_content = f'''
@echo off
cd /d "{base_dir}"
robocopy "{temp_dir}" "{base_dir}" /E /IS /IT /IM /NFL /NDL /NJH /NJS
rd /s /q "{temp_dir}" 2>nul
start "" "{exe_path}"
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

