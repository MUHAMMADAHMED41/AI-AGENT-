from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from voice_assistant.voice_assistant import VoiceAssistant
import os
import time
import speech_recognition as sr
import threading
from gtts import gTTS
import playsound
import tempfile

os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

app = Flask(__name__, template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize voice assistant
assistant = VoiceAssistant()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    try:
        text = request.json.get('text', '')
        print(f"Received text: {text}")
        if text:
            response = assistant.process_command(text)
            return jsonify({
                "userText": text,  # What user typed
                "response": response  # AI's response
            })
        return jsonify({"error": "No text provided"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        print("Processing audio...")
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
            
        audio_file = request.files['audio']
        # Save audio temporarily
        temp_path = "temp_audio.wav"
        audio_file.save(temp_path)
        
        # Process the audio
        text = assistant.process_audio_file(temp_path)  # Add this method to VoiceAssistant
        if text:
            response = assistant.process_command(text)
            # Clean up temp file
            os.remove(temp_path)
            return jsonify({
                "userText": text,
                "response": response
            })
        return jsonify({"error": "No speech detected"}), 400
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        return jsonify({"error": str(e)}), 500

@socketio.on('message')
def handle_message(message):
    try:
        response_stream = assistant.process_command(message)
        for chunk in response_stream:
            emit('response_chunk', {'chunk': chunk})
    except Exception as e:
        emit('error', {'error': str(e)})

@app.route('/current_model', methods=['GET'])
def current_model():
    """API endpoint to get the current model being used."""
    model = assistant.get_current_model()
    return jsonify({"current_model": model})

def process_speech_queue(self):
    """Process speech requests from the queue."""
    while True:
        text = self.speech_queue.get()  # Get the next speech request
        if text is None:  # Exit condition
            break
        try:
            print(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()  # Wait until speaking is finished
        except Exception as e:
            print(f"Error during speech: {e}")
        finally:
            self.speech_queue.task_done()  # Mark the task as done


# Example usage of threading
def example_thread_function():
    print("This is a thread running.")

# Create and start a thread
thread = threading.Thread(target=example_thread_function)
thread.start()

if __name__ == '__main__':
    print("Starting Voice Assistant Web Interface...")
    socketio.run(app, debug=True, port=5000)  # Start the app with SocketIO

    # No need for app.run() here

def speak_text(self, text):
    """Convert text to speech using gTTS."""
    tts = gTTS(text=text, lang='en')
    temp_file_path = "C:\\Users\\ahmaa\\Documents\\output.mp3"  # Change this path to a writable location
    tts.save(temp_file_path)
    playsound.playsound(temp_file_path)  # Play the audio file