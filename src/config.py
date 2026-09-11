import json
import os
from .logger import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

class ConfigManager:
    def __init__(self):
        self.config = {
            "backend": "Ollama",
            "ollama_url": "http://localhost:11434/api/generate",
            "ollama_model": "mistral",
            "lmstudio_url": "http://localhost:1234/v1/chat/completions",
            "lmstudio_model": "local-model",
            "hotkey": "ctrl+alt+g",
            "temperature": 0.3,
            "system_prompt": "ОБЯЗАТЕЛЬНО сохрани исходный язык текста (например, русский). Ничего не придумывай, не переводи, просто исправь грамматические, орфографические и пунктуационные ошибки в следующем тексте. В ответе выведи только исправленный текст без дополнительных комментариев и пояснений:\n\n",
            "copy_delay": 0.3,
            "paste_delay": 0.1,
            "gguf_model_path": "",
            "autostart": False
        }
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for key, value in loaded.items():
                        self.config[key] = value
                logger.info(f"Configuration loaded from {CONFIG_FILE}.")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
        logger.debug(f"Config updated: {key} = {value}")

config_manager = ConfigManager()
