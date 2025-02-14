from voice_assistant import VoiceAssistant
import time

def main():
    assistant = VoiceAssistant()
    print("Voice Assistant initialized. Starting test...")
    
    # Test speaking
    assistant.speak("Hello! I'm your voice assistant. I'm ready to listen.")
    
    try:
        while True:
            print("\nPress Enter to start recording (or 'q' to quit)...")
            user_input = input()
            if user_input.lower() == 'q':
                break
                
            print("Listening... (Press Enter to stop)")
            assistant.listen()
            input()  # Wait for Enter to stop recording
            
            print("Processing...")
            text = assistant.stop_listening()
            print(f"You said: {text}")
            
            if text:
                print("Generating response...")
                response = assistant.process_command(text)
                print(f"Assistant: {response}")
                assistant.speak(response)
            else:
                print("No speech detected")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    
    print("Test completed.")

if __name__ == "__main__":
    main() 