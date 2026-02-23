import winsound
import pyautogui
import webbrowser
import os
import time
import ctypes
import re
import datetime
import screen_brightness_control as sbc
import pywhatkit
import psutil
import shutil
import subprocess
import sys
import pygame
import tkinter as tk
from tkinter import messagebox, simpledialog
from send2trash import send2trash

# --- INITIALIZATION ---
try:
    pygame.mixer.init()
except:
    print("Audio error: Could not start Pygame mixer")

# 🔗 LINK TO YOUR NEW TTS.PY (ElevenLabs + EdgeTTS)
try:
    from tts import speak
except ImportError:
    print("⚠️ Error: tts.py not found. Voice will be disabled.")
    def speak(text): print(f"Silent Mode: {text}")

try:
    import music
except ImportError:
    music = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- APP OPENER WRAPPER ---
try:
    from AppOpener import open as open_app_lib
    def open_app(app_name, match_closest=True, throw_error=True):
        open_app_lib(app_name, match_closest=match_closest, throw_error=throw_error)
except Exception as e:
    print(f"⚠️ AppOpener failed to load (Using fallback): {e}")
    def open_app(app_name, match_closest=True, throw_error=True):
        print(f"Attempting to open {app_name} via OS...")
        clean_name = app_name.strip().lower()
        try:
            subprocess.Popen(f"start {app_name}", shell=True, creationflags=0x08000000)
            time.sleep(0.1)
        except:
            pyautogui.press("win")
            time.sleep(0.1)
            pyautogui.write(clean_name)
            time.sleep(0.5)
            pyautogui.press("enter")

# --- 🗑️ SAFE DELETE (NUCLEAR PROOF) ---
# --- 🧠 SMART PRINT (Code Typing) ---
def smart_print(*args):
    """
    If text looks like code -> TYPE IT (pyautogui).
    If text looks like chat -> SPEAK IT (via tts.py).
    """
    text = " ".join(map(str, args))
    print(f"🖨️ AI Output: {text}")

    # Code Indicators
    code_signals = ["<html", "<!DOCTYPE", "import ", "def ", "class ", "print(", "return", "<div>", "<body>", "{", "}"]
    is_code = any(sig in text for sig in code_signals) or len(text) > 150

    if is_code:
        speak("I am typing the code now. Please click where you want it.")
        time.sleep(2)
        try:
            pyautogui.write(text, interval=0.001) 
        except Exception as e:
            print(f"Typing Error: {e}")
            speak("I could not type the text.")
    else:
        # 🗣️ THIS CALLS YOUR NEW TTS.PY
        speak(text)

def safe_delete(path):
    """
    Safely deletes files. 
    BLOCKS deletion if the file is inside the Aanya App folder.
    """
    path = os.path.abspath(path)
    app_folder = os.path.dirname(os.path.abspath(__file__))
    
    # 🛑 NUCLEAR SAFETY CHECK
    if path.startswith(app_folder):
        print(f"🛑 BLOCKED: Attempted to delete app file: {path}")
        speak("Security Protocol Active. I cannot delete files inside the System Folder.")
        return

    if not os.path.exists(path):
        speak("I cannot find that file.")
        print(f"❌ Path not found: {path}")
        return

    # GUI Confirmation Popup
    root = tk.Tk()
    root.withdraw() 
    root.attributes("-topmost", True)
    
    msg = f"⚠️ CONFIRM DELETE ⚠️\n\nDo you want to send this to Recycle Bin?\n\n📂 {path}"
    confirm = messagebox.askyesno("Confirm Deletion", msg)
    root.destroy()

    if confirm:
        try:
            if 'send2trash' in sys.modules:
                send2trash(path)
                speak("Moved to Recycle Bin.")
            else:
                if os.path.isfile(path): os.remove(path)
                else: shutil.rmtree(path)
                speak("Deleted permanently.")
        except Exception as e:
            speak("Error deleting file.")
            print(e)
    else:
        speak("Cancelled.")

# --- ✨ CREATE FILE/FOLDER ---
def create_file_folder(path, is_folder=False, content=""):
    """Creates a file or folder safely"""
    try:
        path = os.path.abspath(path)
        if os.path.exists(path):
            speak("That file or folder already exists.")
            return

        if is_folder:
            os.makedirs(path)
            print(f"📂 Created Folder: {path}")
            speak("Folder created.")
        else:
            with open(path, "w") as f:
                f.write(content)
            print(f"📄 Created File: {path}")
            speak("File created.")
            
    except Exception as e:
        print(f"❌ Creation Error: {e}")
        speak("I could not create that.")

# --- 🧠 SMART PRINT (Code Typing) ---
def smart_print(*args):
    """
    If text looks like code -> TYPE IT (pyautogui).
    If text looks like chat -> SPEAK IT (tts).
    """
    text = " ".join(map(str, args))
    print(f"🖨️ AI Output: {text}")

    # Code Indicators
    code_signals = ["<html", "<!DOCTYPE", "import ", "def ", "class ", "print(", "return", "<div>", "<body>", "{", "}"]
    is_code = any(sig in text for sig in code_signals) or len(text) > 150

    if is_code:
        speak("I am typing the code now. Please click where you want it.")
        time.sleep(2)
        try:
            pyautogui.write(text, interval=0.001) 
        except Exception as e:
            print(f"Typing Error: {e}")
            speak("I could not type the text.")
    else:
        speak(text)

# --- 🧠 SMART INPUT (Popup) ---
def smart_input(prompt_text):
    """Shows a Popup Window for user input"""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    
    speak(prompt_text) 
    user_input = simpledialog.askstring("Aanya Needs Input", prompt_text)
    root.destroy()
    
    if user_input is None: return ""
    return user_input

# --- ⚡ MAIN PERFORM FUNCTION ---
def perform(intent, alarm_list=None):
    if not intent:
        return

    t = intent.get("type")
    a = intent.get("action")
    p = intent.get("payload")
    ad_free = intent.get("adFree", False)

    print(f"⚙️ Action: {a} | Payload: {p}")
    print(f"⚡ Executing: {t} -> {p}")

    # --- 1. PYTHON EXECUTION ---
    if t == "PYTHON_EXEC":
        try:
            safe_alarm_path = resource_path("alarm.mp3")
            if not os.path.exists(safe_alarm_path):
                print(f"⚠️ WARNING: Alarm file missing at {safe_alarm_path}")

            exec_globals = {
                'os': os, 'sys': sys, 'shutil': shutil, 'subprocess': subprocess,
                'webbrowser': webbrowser, 'pyautogui': pyautogui, 'time': time,
                'datetime': datetime, 'ctypes': ctypes, 
                'print': smart_print,  # 👈 OVERRIDE PRINT
                'speak': speak, 'psutil': psutil, 'winsound': winsound,
                'input': smart_input,  # 👈 OVERRIDE INPUT
                'ALARM_PATH': safe_alarm_path, 'pygame': pygame,
                'safe_delete': safe_delete, 
                'create_file_folder': create_file_folder, 
                'secure_delete': safe_delete # 👈 FIX FOR "secure_delete not defined"
            }

            clean_payload = p
            if "os.remove" in p or "shutil.rmtree" in p:
                clean_payload = p.replace("os.remove", "safe_delete").replace("shutil.rmtree", "safe_delete")

            exec(clean_payload, exec_globals)
            
        except Exception as e:
            print(f"❌ Execution Error: {e}")
            speak("Boss, execution failed.")

    # --- 2. ALARM SYSTEM ---
    elif t == "ALARM" or a == "ALARM_SET":
        if p and alarm_list is not None:
            try:
                command = p.lower()
                target_time = None
                now = datetime.datetime.now()

                numbers = re.findall(r'\d+', command)
                if numbers:
                    amount = int(numbers[0])
                    if "hour" in command: target_time = now + datetime.timedelta(hours=amount)
                    elif "minute" in command: target_time = now + datetime.timedelta(minutes=amount)
                    elif "second" in command: target_time = now + datetime.timedelta(seconds=amount)
                
                if not target_time and (":" in command or "am" in command or "pm" in command):
                    time_match = re.search(r'(\d{1,2})(:(\d{2}))?', command)
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(3)) if time_match.group(3) else 0
                        if "pm" in command and hour != 12: hour += 12
                        if "am" in command and hour == 12: hour = 0
                        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        if target_time < now: target_time += datetime.timedelta(days=1)

                if target_time:
                    alarm_list.append({'time': target_time, 'active': True})
                    print(f"⏰ Alarm set for {target_time}")
                else:
                    print("❌ Could not parse alarm time.")
            except Exception as e:
                print(f"Alarm Error: {e}")

    # --- 3. SYSTEM CONTROL (IMPROVED) ---
    elif t == "SYSTEM":
        # VOLUME LOGIC
        if a == "VOLUME_UP":
            for _ in range(5): pyautogui.press("volumeup")
        elif a == "VOLUME_DOWN":
            for _ in range(5): pyautogui.press("volumedown")
        elif a == "VOLUME_MAX":
            for _ in range(50): pyautogui.press("volumeup")
        elif a == "MUTE" or a == "MUTED":
            pyautogui.press("volumemute")
        elif a == "UNMUTE" or a == "UNMUTED":
            pyautogui.press("volumemute") # Toggle mute off
        elif a == "VOLUME_SET" and p:
            try:
                # Clean input (remove %)
                clean_val = re.sub(r'[^0-9]', '', str(p))
                target = int(clean_val)
                # Mute then scroll up approximation
                pyautogui.press("volumemute")
                for _ in range(50): pyautogui.press("volumedown") # Ensure 0
                presses = int(target / 2)
                for _ in range(presses): pyautogui.press("volumeup")
            except: pass

        # BRIGHTNESS LOGIC
        elif "BRIGHTNESS" in a:
            try:
                current = sbc.get_brightness()
                current = current[0] if current else 50
                
                if a == "BRIGHTNESS_UP": 
                    sbc.set_brightness(min(current + 10, 100))
                elif a == "BRIGHTNESS_DOWN":
                    sbc.set_brightness(max(current - 10, 0))
                elif a == "BRIGHTNESS_MAX":
                    sbc.set_brightness(100)
                elif a == "BRIGHTNESS_MIN":
                    sbc.set_brightness(0)
                elif a == "BRIGHTNESS_SET" and p:
                    # Clean input (remove %)
                    clean_val = re.sub(r'[^0-9]', '', str(p))
                    sbc.set_brightness(int(clean_val))
            except Exception as e:
                print(f"Brightness Error: {e}")

        # OTHER UTILS
        elif a == "LOCK": ctypes.windll.user32.LockWorkStation()
        elif a == "SCREENSHOT": pyautogui.screenshot("screenshot.png")
        elif a == "MINIMIZE": pyautogui.hotkey('win', 'd')
        elif a == "ABORT": os.system("shutdown /a")

        elif a == "TYPE" and p:
            pyautogui.write(p, interval=0.01)
        elif a == "PRESS" and p:
            key = p.replace("window", "win").replace("control", "ctrl").replace("escape", "esc")
            if "+" in key: pyautogui.hotkey(*[k.strip() for k in key.split("+")])
            else: pyautogui.press(key)

    # --- 4. APPS ---
    elif t == "APP":
        if a == "OPEN_URL": webbrowser.open_new_tab(p)
        elif a == "OPEN_APP":
            try: open_app(p, match_closest=True, throw_error=True)
            except: webbrowser.open(f"https://www.google.com/search?q={p}")

    # --- 5. MUSIC ---
    elif t == "MUSIC":
        if a == "PLAY_YT":
            pywhatkit.playonyt(p)
        
        elif a == "PLAY_SPECIFIC":
            link = None
            if music:
                try:
                    mashups = list(music.mashups[0].values()) if isinstance(music.mashups, tuple) else list(music.mashups.values())
                    playlists = list(music.Playlists[0].values()) if isinstance(music.Playlists, tuple) else list(music.Playlists.values())

                    if p == "rahat": link = mashups[3] if ad_free else mashups[0]
                    elif p == "best": link = mashups[4] if ad_free else mashups[1]
                    elif p == "trip": link = mashups[5] if ad_free else mashups[2]
                    elif p == "phonk": link = playlists[2] if ad_free else playlists[0]
                    elif p == "hindi": link = playlists[3] if ad_free else playlists[1]
                    elif p == "english": link = "https://www.youtube.com/watch?v=36YnV9STBqc&list=PLMC9KNkIncKvYin_USF1qoJQnIyMAfRxl" 

                except Exception as e:
                    print(f"Music Lookup Error: {e}")

            if link:
                webbrowser.open(link)
            else:
                print(f"⚠️ Playlist '{p}' not found in library. Searching YouTube...")
                pywhatkit.playonyt(f"{p} songs playlist")