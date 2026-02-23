import tkinter as tk
import requests
import uuid
from session import save_session
import time

# CHANGE THIS: Use http instead of https for localhost
SERVER = "https://aanya-backend.onrender.com"

DEVICE_ID = str(uuid.getnode())

def launch_login():
    root = tk.Tk()
    root.title("Aanya Setup")
    root.geometry("350x300") # Made taller for extra input
    root.resizable(False, False)

    # --- UI Elements ---
    tk.Label(root, text="Aanya Configuration", font=("Segoe UI", 14, "bold")).pack(pady=10)

    # 1. System Access Key
    tk.Label(root, text="System API Key (Access Token)", font=("Segoe UI", 9)).pack()
    sys_key_entry = tk.Entry(root, width=40, font=("Segoe UI", 10))
    sys_key_entry.pack(pady=5)

    # 2. User's Groq Key
    tk.Label(root, text="Your Groq API Key (AI Brain)", font=("Segoe UI", 9)).pack()
    groq_key_entry = tk.Entry(root, width=40, font=("Segoe UI", 10), show="*") # Hides key
    groq_key_entry.pack(pady=5)

    status = tk.Label(root, text="", fg="red", font=("Segoe UI", 9))
    status.pack(pady=5)

    def login():
        sys_key = sys_key_entry.get().strip()
        groq_key = groq_key_entry.get().strip()

        # VALIDATION: Fail if Groq key is missing
        if not sys_key:
            status.config(text="System Key is required")
            return
        if not groq_key:
            status.config(text="Groq API Key is required to run AI")
            return
        if not groq_key.startswith("gsk_"):
            status.config(text="Invalid Groq Key format (must start with gsk_)")
            return

        status.config(text="Verifying Access...", fg="blue")
        root.update()

        try:
                    # FIX: Change command to 'ping' and SEND THE GROQ KEY
                    payload = {
                        "command": "ping", 
                        "email": "Setup_User",
                        "groqKey": groq_key,  # <--- Crucial: Send this so server doesn't crash
                        "deviceId": DEVICE_ID
                    }
                    
                    headers = {"x-api-key": sys_key, "Content-Type": "application/json"}
                    
                    # Send request
                    response = requests.post(f"{SERVER}/command", json=payload, headers=headers, timeout=10)
                    
                    # If successful (200), save and close immediately
                    if response.status_code == 200:
                        session_data = {
                            "apiKey": sys_key,
                            "groqKey": groq_key,
                            "deviceId": DEVICE_ID,
                            "email": "User"
                        }
                        save_session(session_data)
                        root.destroy()
                    
                    # If Limit Exceeded (429), we can choose to let them in anyway 
                    # (Optional: remove this elif if you want to be strict)
                    elif response.status_code == 429:
                        status.config(text="Daily Limit reached, but credentials saved.", fg="orange")
                        # Still save and continue because we know the server exists
                        session_data = {
                            "apiKey": sys_key,
                            "groqKey": groq_key,
                            "deviceId": DEVICE_ID,
                            "email": "User"
                        }
                        save_session(session_data)
                        root.update()
                        time.sleep(1.5)
                        root.destroy()

                    elif response.status_code in [401, 403]:
                        status.config(text="Invalid System Access Key", fg="red")
                    else:
                        status.config(text=f"Server Error: {response.status_code}", fg="red")

        except requests.exceptions.ConnectionError:
            status.config(text="Cannot reach server. Is it running?", fg="red")
        except Exception as e:
            status.config(text=f"Error: {e}", fg="red")

    btn = tk.Button(root, text="Connect System", command=login, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"), width=20)
    btn.pack(pady=15)

    root.mainloop()