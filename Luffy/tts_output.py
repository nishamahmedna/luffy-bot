import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 175)  # Set speech rate (words per minute)

def speak(text):
    """
    Speak the provided text using pyttsx3.
    
    Parameters:
        text (str): The text to be spoken.
    """
    engine.say(text)
    engine.runAndWait()

# For testing purposes:
if __name__ == "__main__":
    speak("Hello, I am Luffy!")
