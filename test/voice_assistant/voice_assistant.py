from voice_assistant.audio_handler import AudioHandler
from voice_assistant.rag_system import RAGSystem
from voice_assistant.llm_handler import LLMHandler
import numpy as np
import speech_recognition as sr
import os
import queue
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'
import pythoncom
from comtypes.client import CreateObject
import threading
from gtts import gTTS
import playsound
import tempfile
import time

class VoiceAssistant:
    def __init__(self):
        print("Initializing voice assistant...")
        self.audio_handler = AudioHandler()
        self.rag_system = RAGSystem()
        self.recognizer = sr.Recognizer()
        
        # Initialize COM in the main thread
        pythoncom.CoInitialize()
        try:
            self.speaker = CreateObject("SAPI.SpVoice")
            print("Speech initialized successfully")
        except Exception as e:
            print(f"Speech initialization error: {e}")
            self.speaker = None
        
        self.llm_handler = LLMHandler(self)  # Pass self to LLMHandler
        self.speech_queue = queue.Queue()  # Create a queue for speech requests
        self.stop_signal = False  # Signal to stop the TTS thread
        self.tts_thread = threading.Thread(target=self.process_speech_queue, daemon=True)
        self.tts_thread.start()  # Start the speech processing thread

        # Optimize recognition settings
        self.recognizer.energy_threshold = 200  # Lower value for higher sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5  # Reduce pause time
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        self.mic_index = 1  # Default microphone
        self.response_queue = queue.Queue()

        self.set_voice()  # Set the voice after initializing the TTS engine

    def set_voice(self):
        """Set a specific voice for TTS."""
        voices = self.speaker.GetVoices()
        if voices:
            self.speaker.Voice = voices[0]
            print(f"Voice set to: {voices[0].GetDescription(0)}")
        else:
            print("No voices available.")

    def speak(self, text):
        """Queue text for speech."""
        if text and not text.isspace():
            print(f"Queueing speech: {text}")
            self.speech_queue.put(text)  # Add text to the queue

    def process_speech_queue(self):
        """Process speech requests from the queue."""
        while not self.stop_signal:
            try:
                text = self.speech_queue.get(timeout=1)  # Wait for 1 second
                if text is None:  # Exit 
                    break
                print(f"Speaking: {text}")
                self.speak_text(text)  # Call the new speak_text method
                self.speech_queue.task_done()
            except queue.Empty:
                continue  # No speech request, continue looping
            except Exception as e:
                print(f"Error during speech: {e}")
                self.speech_queue.task_done()

    def speak_text(self, text):
        """Convert text to speech using gTTS."""
        tts = gTTS(text=text, lang='en')
        # Directly specify the path to the 'test' folder
        temp_file_path = os.path.join('D:\\ai voice agent project\\test', 'output.mp3')
        tts.save(temp_file_path)

        # Use playsound to play the audio file
        playsound.playsound(temp_file_path)  # Play the audio file

    def process_interaction(self):
        start_time = time.time()
        try:
            with sr.Microphone() as source:
                print("\nAdjusting for ambient noise...")
                # Increase adjustment duration and energy threshold
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.recognizer.energy_threshold = 3000  # Increase sensitivity
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 1  # Wait longer for pauses
                
                print("Listening... (Speak now)")
                try:
                    # Increase timeout and phrase time limit
                    audio = self.recognizer.listen(source, 
                                                 timeout=10,  # Longer timeout
                                                 phrase_time_limit=15)  # Longer phrase time
                    
                    print("Processing speech...")
                    text = self.recognizer.recognize_google(audio)  # Use Google's speech recognition
                    print(f"You said: {text}")
                    
                    response = self.process_command(text)
                    print(f"Interaction processed in {time.time() - start_time} seconds")
                    return response
                    
                except sr.WaitTimeoutError:
                    print("No speech detected within timeout period")
                    return "I didn't hear anything. Please try again."
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    return "I couldn't understand that. Please speak more clearly."
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    return "Sorry, there was an error with the speech recognition service."
                    
        except Exception as e:
            print(f"Error in process_interaction: {e}")
            return "An error occurred. Please try again."

    def run(self):
        print("Voice Assistant initialized. Press Ctrl+C to exit.")
        try:
            while True:
                self.process_interaction()
        except KeyboardInterrupt:
            print("\nShutting down voice assistant...")

    def process_command(self, text):
        """Process user command and generate response."""
        try:
            if not text or text.isspace():
                return "Please provide a valid command."
                
            print(f"\nUser: {text}")
            
            # Check for model switch command
            if text.lower().startswith("switch to "):
                model_name = text.lower().replace("switch to ", "").strip()
                switch_response = self.llm_handler.switch_model(model_name)
                self.speak(switch_response)  # Speak the response for model switch
                return switch_response
            
            prompt = f"User: {text}\nAssistant:"
            
            # Generate response using the LLMHandler
            response = self.llm_handler.generate_response(prompt)
            print(f"Generated response: {response}")
            
            # Speak the response
            self.speak(response)  # Queue the response for speech
            
            return response
            
        except Exception as e:
            error_msg = f"Error in model generation: {e}"
            print(error_msg)
            return f"I encountered an error: {str(e)}"
        
    def listen(self):
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = self.recognizer.listen(source, 
                                             timeout=5,  # 5 second timeout
                                             phrase_time_limit=10)  # Adjust as needed
                return audio
        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return None
        except Exception as e:
            print(f"Error during listening: {e}")
            return None
        
    def stop_listening(self):
        self.audio_handler.stop_recording()
        audio_data = self.audio_handler.get_audio_data()
        text = self.audio_handler.transcribe_audio(audio_data)
        return text 

    def process_text(self, text):
        if not text or text.startswith("Error") or text.startswith("Could not"):
            return "I couldn't understand that. Please try again."
        
        print(f"Processing text: {text}")
        response = self.llm_handler.generate_response(text)
        print(f"Response: {response}")
        return response 

    def process_audio_file(self, audio_path):
        try:
            with sr.AudioFile(audio_path) as source:
                print("Processing audio file...")
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized text: {text}")
                return text
        except Exception as e:
            print(f"Error processing audio file: {e}")
            return None 

    def get_current_model(self):
        """Return the name of the current model."""
        return self.llm_handler.get_current_model() 

    def stop(self):
        """Stop the TTS thread."""
        print("Stopping voice assistant...")
        self.stop_signal = True
        self.speech_queue.put(None)  # Unblock the queue
        self.tts_thread.join()
        print("Voice assistant stopped.") 

    def some_method(self):
        from voice_assistant.llm_handler import LLMHandler  # Move import here
        llm_handler = LLMHandler()
        # Use llm_handler as needed

def process_command(command):
    from voice_assistant.voice_assistant import VoiceAssistant  # Move import here
    assistant = VoiceAssistant()
    return assistant.process_command(command) 

def some_method(command):
    from voice_assistant.llm_handler import process_command  # Import here
    response = process_command(command)  # Use process_command
    return response  # Return or process the response as needed 