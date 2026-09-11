import requests
import threading
from .logger import logger
from .config import config_manager

class AIClient:
    def __init__(self):
        self.llm = None
        self.loading_gguf = False
        self.current_gguf_path = None

    def load_gguf_model(self, path):
        if not path or path == self.current_gguf_path:
            return

        def load_thread():
            self.loading_gguf = True
            logger.info(f"Loading GGUF model from {path} in background...")
            try:
                from llama_cpp import Llama
                self.llm = Llama(model_path=path, n_ctx=2048, n_threads=max(1, threading.active_count() - 1))
                self.current_gguf_path = path
                logger.info("GGUF model loaded successfully.")
            except ImportError:
                logger.error("llama_cpp module not found. Please install llama-cpp-python.")
                self.llm = None
                self.current_gguf_path = None
            except Exception as e:
                logger.error(f"Error loading GGUF model: {e}")
                self.llm = None
                self.current_gguf_path = None
            finally:
                self.loading_gguf = False

        threading.Thread(target=load_thread, daemon=True).start()

    def fix_text(self, text, timeout_sec=120):
        prompt_prefix = config_manager.get("system_prompt")
        prompt = f"{prompt_prefix}{text}"

        backend = config_manager.get("backend")
        temperature = float(config_manager.get("temperature"))
        logger.info(f"Sending text to AI via {backend} (Temp: {temperature}, Timeout: {timeout_sec}s)")
        logger.debug(f"Full prompt being sent:\n{prompt}")

        try:
            if backend == "Ollama":
                url = config_manager.get("ollama_url").strip()
                model = config_manager.get("ollama_model").strip()
                response = requests.post(url, json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                }, timeout=timeout_sec)
                response.raise_for_status()

                data = response.json()
                if "response" in data:
                    result = data.get("response", "").strip()
                elif "message" in data and "content" in data["message"]:
                    result = data["message"].get("content", "").strip()
                else:
                    result = ""

                logger.debug(f"Ollama raw response: {result}")
                return result if result else None

            elif backend == "LM Studio":
                url = config_manager.get("lmstudio_url").strip()
                model = config_manager.get("lmstudio_model").strip()
                response = requests.post(url, json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                }, timeout=timeout_sec)
                response.raise_for_status()

                data = response.json()
                logger.debug(f"Raw LM Studio JSON response: {data}")

                message = data["choices"][0]["message"]

                result = message.get("content", "").strip()
                reasoning = message.get("reasoning_content", "").strip()

                if not result and reasoning:
                    logger.info("Main content was empty, extracting from reasoning_content instead.")
                    result = reasoning

                logger.debug(f"Extracted LM Studio response: {result}")
                return result if result else None

            elif backend == "Local GGUF":
                if self.loading_gguf:
                    logger.warning("GGUF model is still loading.")
                    return "Модель еще загружается, пожалуйста подождите..."
                if not self.llm:
                    logger.error("GGUF model not loaded.")
                    return "Ошибка: Модель GGUF не загружена."

                output = self.llm(
                    prompt,
                    max_tokens=512,
                    temperature=temperature,
                    echo=False
                )
                result = output['choices'][0]['text'].strip()
                logger.debug(f"GGUF response: {result}")
                return result if result else None

        except Exception as e:
            logger.error(f"Error communicating with AI: {e}")
            return None

    def test_connection(self, timeout_sec=30):
        backend = config_manager.get("backend")
        logger.info(f"Testing connection for {backend}...")

        try:
            if backend == "Ollama":
                url = config_manager.get("ollama_url").strip()
                model = config_manager.get("ollama_model").strip()
                response = requests.post(url, json={
                    "model": model,
                    "prompt": "Hello",
                    "stream": False
                }, timeout=timeout_sec)
                response.raise_for_status()
                return True, "Успешное подключение к Ollama!"

            elif backend == "LM Studio":
                url = config_manager.get("lmstudio_url").strip()
                models_url = f"{url.rsplit('/chat/completions', 1)[0]}/models"
                response = requests.get(models_url, timeout=timeout_sec)
                response.raise_for_status()
                return True, "Успешное подключение к LM Studio!"

            elif backend == "Local GGUF":
                if self.loading_gguf:
                     return True, "Модель GGUF загружается..."
                if self.llm:
                     return True, "Модель GGUF загружена!"
                return False, "Модель GGUF не загружена (проверьте путь)"

        except Exception as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

ai_client = AIClient()
