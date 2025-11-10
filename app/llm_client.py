import requests
import json

class LLMClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2:latest"
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✓ Connected to Ollama at {self.base_url}")
            else:
                print(f"⚠ Ollama responded with status {response.status_code}")
        except Exception as e:
            print(f"⚠ Could not connect to Ollama: {e}")
            print("Make sure Ollama is running with: ollama serve")
    
    def get_completion_sync(self, prompt, history=None, system_prompt=None):
        """Get a completion from the LLM synchronously"""
        if system_prompt is None:
            system_prompt = "You are Jarvis, a helpful AI assistant. Provide clear, concise, and accurate responses."
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history if provided
        if history:
            for msg in history:
                messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 2000,  # Allow longer responses
                        "temperature": 0.7
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                return f"Error: Ollama returned status {response.status_code}"
                
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"
