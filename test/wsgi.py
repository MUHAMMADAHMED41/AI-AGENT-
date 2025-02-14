from waitress import serve
from app import app
import pyttsx3

def test_tts():
    engine = pyttsx3.init()
    engine.say("Hello, this is a test.")
    engine.runAndWait()  # Wait for the first speech to finish
    engine.say("This is the second test.")
    engine.runAndWait()  # Wait for the second speech to finish

if __name__ == "__main__":
    print("\n=== Voice Assistant Server ===")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Click 'Record' or type your message")
    print("3. Check console for detailed output")
    print("==============================\n")
    test_tts()
    serve(app, host='0.0.0.0', port=5000) 