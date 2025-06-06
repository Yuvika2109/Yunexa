from compileall import compile_path
import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat 
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3

from backend.helper import extract_yt_term, remove_words
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()
# Initialize pygame mixer
pygame.mixer.init()

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    sound_file = r"frontend\assets\audio\start_sound.mp3"  # Using raw string
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    
    
def openCommand(query):
    # Remove assistant name and "open" keyword
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    
    # Clean and prepare the app name
    app_name = query.strip().lower()
    
    if app_name != "":
        try:
            # First try to find in the database
            cursor.execute(
                'SELECT path FROM sys_command WHERE name = ?', (app_name,))
            results = cursor.fetchall()

            if len(results) > 0:
                # If found in database, open using the stored path
                speak("Opening " + app_name)
                os.startfile(results[0][0])
            else:
                # Try web commands
                cursor.execute(
                    'SELECT url FROM web_command WHERE name = ?', (app_name,))
                results = cursor.fetchall()
                
                if len(results) > 0:
                    speak("Opening " + app_name)
                    webbrowser.open(results[0][0])
                else:
                    # For common Windows applications, try direct command
                    speak("Opening " + app_name)
                    
                    # Special handling for common Windows apps
                    if app_name == "notepad":
                        os.system('start notepad')
                    elif app_name == "calculator":
                        os.system('start calc')
                    elif app_name == "paint":
                        os.system('start mspaint')
                    elif app_name == "command prompt" or app_name == "cmd":
                        os.system('start cmd')
                    elif app_name == "file explorer" or app_name == "explorer":
                        os.system('start explorer')
                    elif app_name == "word" or app_name == "microsoft word":
                        os.system('start winword')
                    elif app_name == "excel" or app_name == "microsoft excel":
                        os.system('start excel')
                    elif app_name == "powerpoint" or app_name == "microsoft powerpoint":
                        os.system('start powerpnt')
                    else:
                        # Generic attempt to open
                        try:
                            os.system('start ' + app_name)
                        except:
                            speak(f"I couldn't find {app_name}")
        except Exception as e:
            print(f"Error in openCommand: {e}")
            speak(f"I encountered an error while trying to open {app_name}")


def PlayYoutube(query):
    try:
        search_term = extract_yt_term(query)
        if search_term:
            speak("Playing " + search_term + " on YouTube")
            kit.playonyt(search_term)
        else:
            # Default fallback if extraction fails
            clean_query = query.replace("on youtube", "").strip()
            speak("Playing " + clean_query + " on YouTube")
            kit.playonyt(clean_query)
    except Exception as e:
        print(f"Error in PlayYoutube: {e}")
        speak("I had trouble playing that on YouTube")


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa","yunexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
    
def whatsApp(Phone, message, flag, name):
    # Ensure message is a string
    message = str(message) if message is not None else ""

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to " + name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to " + name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with " + name

    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)


def chatBot(query):
    user_input = query.lower()
    try:
        # Fix the escape sequence by using raw string
        chatbot = hugchat.ChatBot(cookie_path=r"backend\cookies.json")  
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(response)
        speak(response)
        return response
    except Exception as e:
        print(f"Error in chatBot: {e}")
        error_message = "I'm having trouble processing that request right now."
        speak(error_message)
        return error_message