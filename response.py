import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import openai
from dotenv import load_dotenv
import os

# Initialize the speech engine
engine = pyttsx3.init()

# Load environment variables from the .env file
load_dotenv()

# Set up the OpenAI API key from the environment variable
openai.api_key = os.getenv("AIpersonalKey2")  # Replace with the correct variable name from your .env file

# Function to speak a response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen for commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for commands...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return None

# Function to handle commands
def handle_command(command):
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {current_time}.")
    elif "open browser" in command:
        speak("Opening the browser.")
        webbrowser.open("http://www.google.com")
    elif "hello" in command:
        speak("Hello! How can I assist you today?")
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {current_date}.")
    if "calculate" in command:
        expression = command.replace("calculate", "").strip()
        try:
            result = eval(expression)  # Evaluates mathematical expression
            speak(f"The result is {result}.")
        except Exception as e:
            speak("Sorry, I couldn't calculate that.")
    elif "ask" in command:  # Added a new command for asking AI questions
        question = command.replace("ask", "").strip()
        if question:
            response = openai.Completion.create(
                model="gpt-4o-mini",  # usable model
                prompt=question,
                max_tokens=100
            )
            answer = response['choices'][0]['text'].strip()  # checking  response
            speak(f"Here is the answer: {answer}")
        else:
            speak("Please ask a specific question.")
    else:
        speak("Sorry, I didn't recognize that command.")

# Main loop
if __name__ == "__main__":
    while True:
        command = listen()
        if command:
            handle_command(command)