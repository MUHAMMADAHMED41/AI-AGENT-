import requests

class LLMHandler:
    def __init__(self, voice_assistant):
        self.response_cache = {}
        self.ollama_url = "http://localhost:11434/api/generate"
        self.current_model = "llama3.2:latest"  # Default model
        self.voice_assistant = voice_assistant  # Store the voice assistant instance

    def generate_response(self, prompt):
        """Generate response using the specified model via Ollama API"""
        if prompt in self.response_cache:
            return self.response_cache[prompt]

        try:
            payload = {
                "model": self.current_model,  # Use the current model
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.95
            }
            print("Sending request to Ollama...")
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            result = response.json()['response'].strip()
            print(f"Response received: {result[:100]}...")  # Print first 100 chars
            self.response_cache[prompt] = result
            self.voice_assistant.speak(result)  # Use the speak method to vocalize the response
            return result
            
        except requests.exceptions.ConnectionError:
            print("Error: Cannot connect to Ollama. Is it running?")
            return "Error: Ollama service not running. Please start with 'ollama serve'"
        except Exception as e:
            print(f"Ollama API error: {e}")
            return f"Error connecting to Ollama API: {str(e)}"

    def switch_model(self, model_name):
        """Switch to a different model"""
        available_models = ["qwen2:latest", "llama3.2:latest", "deepseek-r1:7b"]
        if model_name in available_models:
            self.current_model = model_name
            return f"Switched to {model_name}"
        else:
            return f"Unknown model: {model_name}"

    def get_current_model(self):
        """Return the name of the current model."""
        return self.current_model