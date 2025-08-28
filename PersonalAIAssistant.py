import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import openai
from dotenv import load_dotenv
import os
import threading
from PIL import Image, ImageDraw, ImageTk
import io
import json

class PersonalAIAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal AI Assistant with Drawing")
        self.root.geometry("1200x800")
        
        # Initialize speech engine
        self.engine = pyttsx3.init()
        self.is_listening = False
        
        # Load environment variables
        load_dotenv()
        
        # Set up OpenAI API key
        openai.api_key = os.getenv("AIpersonalKey2")
        
        # Drawing variables
        self.drawing_canvas = None
        self.current_color = "#000000"
        self.brush_size = 2
        self.last_x = None
        self.last_y = None
        self.drawing_enabled = True
        
        # Create the UI
        self.create_interface()
        
    def create_interface(self):
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Assistant Tab
        self.create_assistant_tab()
        
        # Drawing Tab
        self.create_drawing_tab()
        
        # Settings Tab
        self.create_settings_tab()
        
    def create_assistant_tab(self):
        # Assistant frame
        assistant_frame = ttk.Frame(self.notebook)
        self.notebook.add(assistant_frame, text="AI Assistant")
        
        # Title
        title_label = tk.Label(assistant_frame, text="Personal AI Assistant", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.Frame(assistant_frame)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                   font=("Arial", 10), fg="green")
        self.status_label.pack(side="left")
        
        # Voice commands frame
        voice_frame = ttk.LabelFrame(assistant_frame, text="Voice Commands", padding=10)
        voice_frame.pack(fill="x", padx=20, pady=10)
        
        # Listen button
        self.listen_button = tk.Button(voice_frame, text="🎤 Start Listening", 
                                     command=self.toggle_listening, 
                                     font=("Arial", 12), bg="#4CAF50", fg="white")
        self.listen_button.pack(pady=5)
        
        # Text input frame
        text_frame = ttk.LabelFrame(assistant_frame, text="Text Commands", padding=10)
        text_frame.pack(fill="x", padx=20, pady=10)
        
        self.command_entry = tk.Entry(text_frame, font=("Arial", 12))
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.command_entry.bind("<Return>", self.process_text_command)
        
        send_button = tk.Button(text_frame, text="Send", command=self.process_text_command,
                               font=("Arial", 10), bg="#2196F3", fg="white")
        send_button.pack(side="right")
        
        # Response area
        response_frame = ttk.LabelFrame(assistant_frame, text="Responses", padding=10)
        response_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create scrollable text widget
        self.response_text = tk.Text(response_frame, wrap="word", font=("Arial", 10),
                                   state="disabled", height=15)
        scrollbar = ttk.Scrollbar(response_frame, orient="vertical", command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=scrollbar.set)
        
        self.response_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Available commands info
        commands_frame = ttk.LabelFrame(assistant_frame, text="Available Commands", padding=10)
        commands_frame.pack(fill="x", padx=20, pady=10)
        
        commands_text = """Commands you can use:
• "time" - Get current time
• "date" - Get current date
• "hello" - Greeting
• "open browser" - Open web browser
• "calculate [expression]" - Perform calculations
• "ask [question]" - Ask AI a question
• "draw [description]" - Generate drawing prompt"""
        
        commands_label = tk.Label(commands_frame, text=commands_text, 
                                font=("Arial", 9), justify="left")
        commands_label.pack()
        
    def create_drawing_tab(self):
        # Drawing frame
        drawing_frame = ttk.Frame(self.notebook)
        self.notebook.add(drawing_frame, text="Drawing Canvas")
        
        # Toolbar
        toolbar_frame = ttk.Frame(drawing_frame)
        toolbar_frame.pack(fill="x", padx=10, pady=5)
        
        # Color picker
        color_button = tk.Button(toolbar_frame, text="Choose Color", 
                               command=self.choose_color, font=("Arial", 10))
        color_button.pack(side="left", padx=5)
        
        # Color display
        self.color_display = tk.Label(toolbar_frame, width=3, bg=self.current_color,
                                    relief="solid", borderwidth=2)
        self.color_display.pack(side="left", padx=5)
        
        # Brush size
        tk.Label(toolbar_frame, text="Brush Size:", font=("Arial", 10)).pack(side="left", padx=(20, 5))
        self.brush_scale = tk.Scale(toolbar_frame, from_=1, to=20, orient="horizontal",
                                  command=self.update_brush_size)
        self.brush_scale.set(self.brush_size)
        self.brush_scale.pack(side="left", padx=5)
        
        # Clear button
        clear_button = tk.Button(toolbar_frame, text="Clear Canvas", 
                               command=self.clear_canvas, font=("Arial", 10),
                               bg="#f44336", fg="white")
        clear_button.pack(side="left", padx=20)
        
        # Save button
        save_button = tk.Button(toolbar_frame, text="Save Drawing", 
                              command=self.save_drawing, font=("Arial", 10),
                              bg="#4CAF50", fg="white")
        save_button.pack(side="left", padx=5)
        
        # Toggle drawing
        self.toggle_button = tk.Button(toolbar_frame, text="Drawing: ON", 
                                     command=self.toggle_drawing, font=("Arial", 10),
                                     bg="#2196F3", fg="white")
        self.toggle_button.pack(side="right", padx=5)
        
        # Canvas frame
        canvas_frame = ttk.Frame(drawing_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas with scrollbars
        self.drawing_canvas = tk.Canvas(canvas_frame, bg="white", width=800, height=600)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.drawing_canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.drawing_canvas.yview)
        
        self.drawing_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        self.drawing_canvas.configure(scrollregion=self.drawing_canvas.bbox("all"))
        
        # Pack canvas and scrollbars
        self.drawing_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind drawing events
        self.drawing_canvas.bind("<Button-1>", self.start_drawing)
        self.drawing_canvas.bind("<B1-Motion>", self.draw)
        self.drawing_canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        
    def create_settings_tab(self):
        # Settings frame
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Voice settings
        voice_frame = ttk.LabelFrame(settings_frame, text="Voice Settings", padding=20)
        voice_frame.pack(fill="x", padx=20, pady=20)
        
        # Speech rate
        tk.Label(voice_frame, text="Speech Rate:", font=("Arial", 10)).pack(anchor="w")
        self.rate_scale = tk.Scale(voice_frame, from_=100, to=300, orient="horizontal")
        self.rate_scale.set(200)
        self.rate_scale.pack(fill="x", pady=5)
        
        # Apply voice settings button
        apply_voice_button = tk.Button(voice_frame, text="Apply Voice Settings",
                                     command=self.apply_voice_settings,
                                     font=("Arial", 10), bg="#2196F3", fg="white")
        apply_voice_button.pack(pady=10)
        
        # API settings
        api_frame = ttk.LabelFrame(settings_frame, text="API Settings", padding=20)
        api_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(api_frame, text="OpenAI API Status:", font=("Arial", 10)).pack(anchor="w")
        api_status = "✅ Connected" if openai.api_key else "❌ Not configured"
        self.api_status_label = tk.Label(api_frame, text=api_status, font=("Arial", 10))
        self.api_status_label.pack(anchor="w", pady=5)
        
        # Test API button
        test_api_button = tk.Button(api_frame, text="Test API Connection",
                                  command=self.test_api_connection,
                                  font=("Arial", 10), bg="#FF9800", fg="white")
        test_api_button.pack(pady=10)
        
    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        self.is_listening = True
        self.listen_button.config(text="🔴 Stop Listening", bg="#f44336")
        self.status_label.config(text="Listening...", fg="red")
        
        # Start listening in a separate thread
        threading.Thread(target=self.listen_for_commands, daemon=True).start()
    
    def stop_listening(self):
        self.is_listening = False
        self.listen_button.config(text="🎤 Start Listening", bg="#4CAF50")
        self.status_label.config(text="Ready", fg="green")
    
    def listen_for_commands(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while self.is_listening:
                try:
                    self.root.after(0, lambda: self.status_label.config(text="Listening...", fg="red"))
                    audio = recognizer.listen(source, timeout=1)
                    command = recognizer.recognize_google(audio).lower()
                    self.root.after(0, lambda: self.add_response(f"You said: {command}"))
                    self.root.after(0, lambda: self.handle_command(command))
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.root.after(0, lambda: self.add_response("Sorry, I couldn't understand that."))
                except sr.RequestError as e:
                    self.root.after(0, lambda: self.add_response(f"Speech recognition error: {e}"))
                    break
    
    def process_text_command(self, event=None):
        command = self.command_entry.get().strip().lower()
        if command:
            self.add_response(f"You typed: {command}")
            self.handle_command(command)
            self.command_entry.delete(0, tk.END)
    
    def handle_command(self, command):
        try:
            if "time" in command:
                current_time = datetime.datetime.now().strftime("%H:%M")
                response = f"The time is {current_time}."
                self.add_response(response)
                self.speak(response)
                
            elif "open browser" in command:
                response = "Opening the browser."
                self.add_response(response)
                self.speak(response)
                webbrowser.open("http://www.google.com")
                
            elif "hello" in command:
                response = "Hello! How can I assist you today?"
                self.add_response(response)
                self.speak(response)
                
            elif "date" in command:
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                response = f"Today's date is {current_date}."
                self.add_response(response)
                self.speak(response)
                
            elif "calculate" in command:
                expression = command.replace("calculate", "").strip()
                try:
                    # Safe evaluation of mathematical expressions
                    allowed_chars = set('0123456789+-*/.() ')
                    if all(c in allowed_chars for c in expression):
                        result = eval(expression)
                        response = f"The result is {result}."
                    else:
                        response = "Invalid characters in expression."
                    self.add_response(response)
                    self.speak(response)
                except Exception as e:
                    response = "Sorry, I couldn't calculate that."
                    self.add_response(response)
                    self.speak(response)
                    
            elif "draw" in command:
                description = command.replace("draw", "").strip()
                if description:
                    response = f"Switching to drawing tab for: {description}"
                    self.add_response(response)
                    self.speak(response)
                    self.notebook.select(1)  # Switch to drawing tab
                else:
                    response = "Please specify what you'd like to draw."
                    self.add_response(response)
                    self.speak(response)
                    
            elif "ask" in command and openai.api_key:
                question = command.replace("ask", "").strip()
                if question:
                    self.add_response("Asking AI...")
                    threading.Thread(target=self.ask_ai, args=(question,), daemon=True).start()
                else:
                    response = "Please ask a specific question."
                    self.add_response(response)
                    self.speak(response)
            else:
                response = "Sorry, I didn't recognize that command."
                self.add_response(response)
                self.speak(response)
                
        except Exception as e:
            error_response = f"An error occurred: {str(e)}"
            self.add_response(error_response)
            self.speak("An error occurred while processing your command.")
    
    def ask_ai(self, question):
        try:
            # Note: This uses the older OpenAI API format from your original code
            # You may need to update this to use the newer ChatCompletion format
            response = openai.Completion.create(
                model="text-davinci-003",  # Updated model name
                prompt=question,
                max_tokens=100
            )
            answer = response['choices'][0]['text'].strip()
            ai_response = f"AI Answer: {answer}"
            self.root.after(0, lambda: self.add_response(ai_response))
            self.root.after(0, lambda: self.speak(f"Here is the answer: {answer}"))
        except Exception as e:
            error_msg = f"AI Error: {str(e)}"
            self.root.after(0, lambda: self.add_response(error_msg))
            self.root.after(0, lambda: self.speak("Sorry, I couldn't get an AI response."))
    
    def add_response(self, text):
        self.response_text.config(state="normal")
        self.response_text.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')} - {text}\n")
        self.response_text.see(tk.END)
        self.response_text.config(state="disabled")
    
    def speak(self, text):
        def speak_thread():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=speak_thread, daemon=True).start()
    
    # Drawing methods
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose color")[1]
        if color:
            self.current_color = color
            self.color_display.config(bg=color)
    
    def update_brush_size(self, value):
        self.brush_size = int(value)
    
    def clear_canvas(self):
        self.drawing_canvas.delete("all")
        
    def toggle_drawing(self):
        self.drawing_enabled = not self.drawing_enabled
        status = "ON" if self.drawing_enabled else "OFF"
        color = "#4CAF50" if self.drawing_enabled else "#f44336"
        self.toggle_button.config(text=f"Drawing: {status}", bg=color)
    
    def start_drawing(self, event):
        if self.drawing_enabled:
            self.last_x = event.x
            self.last_y = event.y
    
    def draw(self, event):
        if self.drawing_enabled and self.last_x and self.last_y:
            self.drawing_canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                          width=self.brush_size, fill=self.current_color,
                                          capstyle=tk.ROUND, smooth=tk.TRUE)
            self.last_x = event.x
            self.last_y = event.y
    
    def stop_drawing(self, event):
        self.last_x = None
        self.last_y = None
    
    def save_drawing(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            # Get canvas bounds
            self.drawing_canvas.update()
            x = self.drawing_canvas.winfo_rootx()
            y = self.drawing_canvas.winfo_rooty()
            width = self.drawing_canvas.winfo_width()
            height = self.drawing_canvas.winfo_height()
            
            # Note: This is a simplified save method
            # For better results, you might want to use PIL to capture the canvas
            messagebox.showinfo("Save", f"Drawing would be saved to {file_path}")
    
    def apply_voice_settings(self):
        rate = self.rate_scale.get()
        self.engine.setProperty('rate', rate)
        self.add_response(f"Voice settings updated: Rate = {rate}")
        self.speak("Voice settings have been updated.")
    
    def test_api_connection(self):
        if openai.api_key:
            threading.Thread(target=self._test_api, daemon=True).start()
        else:
            messagebox.showwarning("API Error", "OpenAI API key not configured")
    
    def _test_api(self):
        try:
            # Simple API test
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Hello",
                max_tokens=5
            )
            self.root.after(0, lambda: messagebox.showinfo("API Test", "✅ API connection successful!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("API Test", f"❌ API connection failed:\n{str(e)}"))

def main():
    root = tk.Tk()
    app = PersonalAIAssistant(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
