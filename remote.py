import socketio
import time

sio = socketio.Client()
API_KEY = ""
SERVER_URL = ""
process_command_callback = None

@sio.event
def connect():
    print("\n🟢 Connected to Aanya Remote Server!")
    sio.emit("join_room", {"apiKey": API_KEY, "role": "pc"})

# 1. Listen for "send_command" instead of execute_command
@sio.on("send_command")
def handle_command(data):
    # Safely extract the command whether your Node server forwards a dict or just the string
    command = data.get("command") if isinstance(data, dict) else data
    
    print(f"\n📱 Phone Command Received: {command}")
    
    if process_command_callback:
        reply = process_command_callback(command)
        
        # 2. Emit "receive_response" to match the React app
        sio.emit("receive_response", {"apiKey": API_KEY, "reply": str(reply)})

@sio.event
def disconnect():
    print("\n🔴 Disconnected from Remote Server.")

def start_remote_listener(api_key, server_url, callback_function):
    """
    Starts the socket connection in the background.
    """
    global API_KEY, SERVER_URL, process_command_callback
    API_KEY = api_key
    SERVER_URL = server_url
    process_command_callback = callback_function
    
    # Retry loop just in case your internet drops or server is sleeping
    while True:
        try:
            if not sio.connected:
                sio.connect(SERVER_URL)
                sio.wait()
        except Exception as e:
            print(f"⚠️ Remote Link failed to connect: {e}. Retrying in 10s...")
            time.sleep(10)