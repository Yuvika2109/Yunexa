import time 
import pyttsx3 
import speech_recognition as sr 
import eel  

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
         
    # Check how many voices are available and use an appropriate index
    voice_index = 0  # Default to first voice
    if len(voices) > 2:  # Only use index 2 if it exists
        voice_index = 2
    elif len(voices) > 0:  # Otherwise use whatever is available
        voice_index = 0
             
    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', 174)  # Set rate before speaking for consistency
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()
    eel.receiverText(text)

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 8)
         
        try:
            print("Recognizing...")
            eel.DisplayMessage("Recognizing...")
            query = r.recognize_google(audio, language='en-US')
            print(f"User said: {query}\n")
            eel.DisplayMessage(f"User said: {query}")
            return query.lower()
        except Exception as e:
            print(f"Error: {str(e)}\n")
            return None

@eel.expose
def return_value(call_id):
    """Handle Eel's value return expectations"""
    return {'status': 'ok', 'value': None}
         
@eel.expose 
def takeAllCommands(message=None):
    try:
        if message is None:
            query = takecommand()  # If no message is passed, listen for voice input
            if not query:
                eel.ShowHood()
                return  # Exit if no query is received
            print(query)
            eel.senderText(query)
        else:
            query = message  # If there's a message, use it
            print(f"Message received: {query}")
            eel.senderText(query)
         
        if query:
            if "open" in query:
                from backend.feature import openCommand
                openCommand(query)
            elif "send message" in query or "call" in query or "video call" in query:
                from backend.feature import findContact, whatsApp
                flag = ""
                Phone, name = findContact(query)
                if Phone != 0:
                    if "send message" in query:
                        flag = 'message'
                        speak("What message to send?")
                        message_query = takecommand()  # Ask for the message text
                        if message_query is None:
                            message_query = ""  # Provide empty string if None
                    elif "call" in query:
                        flag = 'call'
                        message_query = ""
                    else:
                        flag = 'video call'
                        message_query = ""
                    whatsApp(Phone, message_query, flag, name)
            elif "on youtube" in query:
                from backend.feature import PlayYoutube
                PlayYoutube(query)
            else:
                from backend.feature import chatBot
                chatBot(query)
        else:
            speak("No command was given.")
    except Exception as e:
        print(f"An error occurred: {e}")
        speak("Sorry, something went wrong.")
         
    eel.ShowHood()