import os
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

from voice_assistant.voice_assistant import VoiceAssistant

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("🤖 Welcome to Voice Assistant!")
    print("=" * 50)
    print("Commands:")
    print("- Press ENTER to start listening")
    print("- Type 'exit' to quit")
    print("=" * 50)

    assistant = VoiceAssistant()
    assistant.speak("Hello, this is a test.")  # Example usage

    while True:
        try:
            command = input("\n🎤 Press ENTER to speak (or type 'exit'): ")
            
            if command.lower() == 'exit':
                print("\nGoodbye! 👋")
                break

            assistant.process_interaction()
            print("\n" + "=" * 50)

        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            continue

if __name__ == "__main__":
    main() 