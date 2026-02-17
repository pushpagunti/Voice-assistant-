import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import datetime
import openai
from transformers import pipeline
import threading
import time

# Set your OpenAI API key
openai.api_key = "your-api-key-here"

engine = pyttsx3.init()
sentiment_analyzer = pipeline("sentiment-analysis")

context = [
    {"role": "system", "content": "You're Pushpa's helpful AI voice assistant."},
    {"role": "user", "content": "My name is Pushpa."}
]

chat_history = []
task_history = []

def speak(text):
    engine.say(text)
    engine.runAndWait()

def detect_sentiment(text):
    result = sentiment_analyzer(text)[0]
    return f"You seem {result['label'].lower()} ({round(result['score'] * 100)}% confidence)."

def ask_ai(prompt):
    context.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=context
    )
    reply = response.choices[0].message["content"]
    context.append({"role": "assistant", "content": reply})
    return reply

def execute_command(command):
    command = command.lower()
    
    if 'open youtube' in command:
        webbrowser.open("https://youtube.com")
        log_task("Opened YouTube")
        return "Opening YouTube."
    elif 'play music' in command:
        music_dir = 'C:\\Users\\Pushpa\\Music'
        try:
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))
            log_task("Played music")
            return "Playing music."
        except:
            return "Music folder not found."
    elif 'what is my mood' in command:
        mood = detect_sentiment(command)
        log_task("Checked mood")
        return mood
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        log_task("Told time")
        return f"The time is {current_time}."
    elif 'open calculator' in command:
        os.system('calc')
        log_task("Opened Calculator")
        return "Opening calculator."
    elif 'open notepad' in command:
        os.system('notepad')
        log_task("Opened Notepad")
        return "Opening notepad."
    elif 'open folder' in command:
        os.system('explorer C:\\Users\\Pushpa\\Documents')
        log_task("Opened Folder")
        return "Opening your documents folder."
    elif 'search google for' in command:
        query = command.replace('search google for', '').strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        log_task(f"Searched Google for: {query}")
        return f"Searching Google for {query}."
    elif 'search youtube for' in command:
        query = command.replace('search youtube for', '').strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        log_task(f"Searched YouTube for: {query}")
        return f"Searching YouTube for {query}."
    elif 'hospital website' in command:
        webbrowser.open("https://www.apollohospitals.com/")
        log_task("Opened hospital site")
        return "Opening hospital website."
    elif 'exit' in command or 'quit' in command:
        speak("Goodbye Pushpa!")
        save_logs()
        app.quit()
    else:
        return None

def log_chat(user, bot):
    chat_history.append(f"You: {user}\nAssistant: {bot}\n")

def log_task(task):
    task_history.append(f"{datetime.datetime.now()}: {task}")

def save_logs():
    with open("chat_log.txt", "w") as f:
        f.write("\n".join(chat_history))
    with open("task_log.txt", "w") as f:
        f.write("\n".join(task_history))

def listen_once():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

def hotword_listener():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                print("Waiting for hotword 'hey assistant'...")
                audio = r.listen(source)
                hotword = r.recognize_google(audio).lower()
                if "hey assistant" in hotword:
                    speak("Yes Pushpa, I'm listening...")
                    user_input = listen_once().strip()
                    if user_input:
                        chat_window.insert(tk.END, f"\nYou: {user_input}")
                        process_input(user_input)
            except:
                pass

def process_input(user_input):
    response = execute_command(user_input)
    if response:
        chat_window.insert(tk.END, f"\nAssistant: {response}")
        speak(response)
        log_chat(user_input, response)
    else:
        ai_reply = ask_ai(user_input)
        chat_window.insert(tk.END, f"\nAssistant: {ai_reply}")
        speak(ai_reply)
        log_chat(user_input, ai_reply)

# GUI SETUP
app = tk.Tk()
app.title("Pushpa's Smart Voice Assistant")
app.geometry("600x500")
app.configure(bg="#f0f0f0")

title_label = tk.Label(app, text="Pushpa's Assistant", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

chat_window = scrolledtext.ScrolledText(app, width=70, height=20, wrap=tk.WORD, font=("Courier", 10))
chat_window.pack(padx=10, pady=10)

def manual_listen():
    threading.Thread(target=manual_listen_thread).start()

def manual_listen_thread():
    user_input = listen_once().strip()
    if user_input:
        chat_window.insert(tk.END, f"\nYou: {user_input}")
        process_input(user_input)

mic_button = tk.Button(app, text="Speak", font=("Helvetica", 14), bg="#b3e6ff", command=manual_listen)
mic_button.pack(pady=10)

exit_button = tk.Button(app, text="Exit", font=("Helvetica", 12), bg="#ffcccc", command=lambda: [save_logs(), app.quit()])
exit_button.pack(pady=5)

# Start hotword listener in background
threading.Thread(target=hotword_listener, daemon=True).start()

app.mainloop()
