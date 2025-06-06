import os
import eel
from backend.auth import recoganize
from backend.auth.recoganize import AuthenticateFace
from backend.feature import *
from backend.command import *

# Override Eel's _process_message function to handle missing 'value' keys
original_process_message = eel._process_message

def patched_process_message(message, websocket):
    try:
        if 'return' in message and 'call_id' in message and 'value' not in message:
            # Add a value key if missing
            message['value'] = None
        return original_process_message(message, websocket)
    except Exception as e:
        print(f"Error processing message: {e}")
        return None

eel._process_message = patched_process_message

def start():
    # Initialize eel with your frontend directory
    eel.init("frontend")
    play_assistant_sound()
    
    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome to Yunexa")
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
    
    # Start the browser AFTER initializing eel but BEFORE starting the server
    port = 8000  # Choose a port you prefer
    os.system(f'start msedge.exe --app="http://localhost:{port}/index.html"')
    
    # Now start the eel server
    eel.start("index.html", mode=None, host="localhost", port=port, block=True)

