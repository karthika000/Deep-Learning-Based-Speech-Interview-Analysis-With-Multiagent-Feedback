import os
import requests
from dotenv import load_dotenv

class OllamaClient:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
        }
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "Could not connect to Ollama. Make sure Ollama is running. \n"
                "Try running: ollama serve\n"
                f"Error details: {e}"
            )
        except requests.exceptions.Timeout as e:
            raise RuntimeError(
                "Request to Ollama timed out. The model might be taking too long to respond. \n"
                "Try increasing the timeout or checking the model's performance. \n"
                f"Error details: {e}"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Ollama request failed: {e}"
            )
        
def get_llm_client():
    backend = os.getenv("LLM_BACKEND", "ollama").lower()
    if backend == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unsupported LLM_BACKEND: {backend}. Supported backends: ollama")