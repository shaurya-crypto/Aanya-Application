import requests

import sys

import os

import subprocess

import time

import tkinter as tk

from tkinter import ttk, messagebox

import threading



# --- CONFIGURATION ---

VERSION_URL = "https://aanya-backend.onrender.com/version"



# Import version from config.py

try:

    from config import APP_VERSION

except ImportError:

    print("⚠️ Config not found, using fallback version.")

    APP_VERSION = "0.0.0"



def check_for_update():

    """Checks the online JSON file for a newer version."""

    try:

        print(f"Checking for updates from {VERSION_URL}...")

        print(f"Current Version: {APP_VERSION}")

       

        response = requests.get(VERSION_URL, timeout=5)

        response.raise_for_status()

        data = response.json()

       

        latest_version = data.get("version")

        download_url = data.get("url")



        if latest_version is None:

            print("Update Check Failed: 'version' key missing.")

            return {"update": False}



        if latest_version > APP_VERSION:

            print(f"New version found: {latest_version}")

            return {"update": True, "latest": latest_version, "url": download_url}

       

        print("Aanya is up to date.")

        return {"update": False}

    except Exception as e:

        print(f"Update Check Error: {e}")

        return {"update": False}



def show_progress_gui(url, latest_version):

    """Downloads file with a GUI Progress Bar."""

   

    # Create popup window

    progress_win = tk.Tk()

    progress_win.title("Updating Aanya...")

   

    # Center the window

    window_width = 350

    window_height = 150

    screen_width = progress_win.winfo_screenwidth()

    screen_height = progress_win.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)

    y = (screen_height // 2) - (window_height // 2)

    progress_win.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

    progress_win.resizable(False, False)

   

    # Keep window on top

    progress_win.attributes("-topmost", True)



    # Label

    lbl = tk.Label(progress_win, text=f"Downloading Update v{latest_version}...", font=("Arial", 10), pady=10)

    lbl.pack()



    # Progress Bar

    progress_var = tk.DoubleVar()

    bar = ttk.Progressbar(progress_win, variable=progress_var, maximum=100)

    bar.pack(fill=tk.X, padx=25, pady=5)



    # Percentage Label

    percent_lbl = tk.Label(progress_win, text="0%")

    percent_lbl.pack()



    def run_download():

        try:

            new_filename = f"aanya_v{latest_version}.exe"

            response = requests.get(url, stream=True)

            total_size = int(response.headers.get('content-length', 0))

            downloaded = 0



            with open(new_filename, 'wb') as f:

                for chunk in response.iter_content(chunk_size=4096):

                    if chunk:

                        f.write(chunk)

                        downloaded += len(chunk)

                       

                        if total_size > 0:

                            percent = (downloaded / total_size) * 100

                            # Schedule UI updates on main thread

                            progress_win.after(0, lambda p=percent: update_bar(p))



            # --- DOWNLOAD FINISHED ---

            # Don't close yet! Update status instead.

            progress_win.after(0, lambda: lbl.config(text="Verifying & Installing..."))

            progress_win.after(0, lambda: bar.config(mode='indeterminate'))

            progress_win.after(0, lambda: bar.start(10))

           

            # Wait a moment for UX

            time.sleep(1)

           

            # Run swap script (Pass the window so we can close it later)

            progress_win.after(0, lambda: start_swap_script(new_filename, progress_win))



        except Exception as e:

            progress_win.after(0, lambda: messagebox.showerror("Update Failed", f"Download Error: {e}"))

            progress_win.after(0, progress_win.destroy)



    def update_bar(percent):

        progress_var.set(percent)

        percent_lbl.config(text=f"{int(percent)}%")



    # Run download in a separate thread

    threading.Thread(target=run_download, daemon=True).start()

    progress_win.mainloop()



# Add this import at the top if missing
import os 

def start_swap_script(new_filename, progress_win=None):
    try:
        print("Download complete. Launching Installer...")
        installer_path = os.path.abspath(new_filename)
        
        # --- TEST MODE CHECK ---
        if not getattr(sys, 'frozen', False):
            messagebox.showinfo("Test Mode", f"Installer downloaded to:\n{installer_path}")
            return

        # Launch the installer
        subprocess.Popen([installer_path, "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"])
        
        # ⚠️ CRITICAL CHANGE: Use os._exit(0) instead of sys.exit()
        # This kills the process INSTANTLY without waiting for cleanup.
        # This releases the file lock immediately.
        os._exit(0)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch update: {e}")