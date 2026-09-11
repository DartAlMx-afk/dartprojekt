import requests
from .logger import logger
from .config import config_manager

class AIClient:
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

        except Exception as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

ai_client = AIClient()
