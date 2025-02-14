import tkinter as tk
from tkinter import ttk, scrolledtext
from voice_assistant.voice_assistant import VoiceAssistant
import threading
import queue

class VoiceAssistantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Assistant")
        self.root.geometry("600x400")
        
        self.assistant = VoiceAssistant()
        self.is_listening = False
        self.message_queue = queue.Queue()
        
        self.create_widgets()
        self.update_messages()
        
    def create_widgets(self):
        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=15)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Record button
        self.record_button = ttk.Button(
            button_frame, 
            text="🎤 Start Recording", 
            command=self.toggle_recording
        )
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Ready")
        self.status_label.pack(pady=5)
        
    def toggle_recording(self):
        if not self.is_listening:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_listening = True
        self.record_button.configure(text="⏹ Stop Recording")
        self.status_label.configure(text="Listening...")
        self.update_chat("🎤 Listening...")
        
        # Start recording in a separate thread
        threading.Thread(target=self.assistant.listen, daemon=True).start()
        
    def stop_recording(self):
        self.is_listening = False
        self.record_button.configure(text="🎤 Start Recording")
        self.status_label.configure(text="Processing...")
        
        def process_audio():
            text = self.assistant.stop_listening()
            if text:
                self.update_chat(f"You: {text}")
                self.status_label.configure(text="Generating response...")
                
                response = self.assistant.process_command(text)
                self.update_chat(f"Assistant: {response}")
                
                # Speak response in a separate thread
                threading.Thread(
                    target=self.assistant.speak, 
                    args=(response,), 
                    daemon=True
                ).start()
                
            self.status_label.configure(text="Ready")
            
        threading.Thread(target=process_audio, daemon=True).start()
        
    def update_chat(self, message):
        self.message_queue.put(message)
        
    def update_messages(self):
        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                self.chat_area.insert(tk.END, message + "\n")
                self.chat_area.see(tk.END)
            self.root.update()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceAssistantGUI()
    app.run() 