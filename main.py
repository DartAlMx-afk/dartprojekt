import keyboard
import pyperclip
import requests
import time
import sys

# Настройки Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral" # Можно изменить на qwen, llama3 и т.д.

def fix_text(text):
    prompt = f"Исправь грамматические, орфографические и пунктуационные ошибки в следующем тексте. В ответе выведи только исправленный текст без дополнительных комментариев и пояснений:\n\n{text}"

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ошибка при обращении к ИИ: {e}")
        return None

def on_hotkey():
    print("Горячая клавиша нажата!")

    # Сохраняем предыдущее содержимое буфера обмена
    original_clipboard = pyperclip.paste()

    # Очищаем буфер обмена, чтобы убедиться, что мы скопировали новый текст
    pyperclip.copy("")

    # Отпускаем клавиши-модификаторы, чтобы они не мешали Ctrl+C
    keyboard.release("ctrl")
    keyboard.release("g")

    # Имитируем Ctrl+C для копирования выделенного текста
    keyboard.send("ctrl+c")
    time.sleep(0.2) # Ждем, чтобы текст успел скопироваться в буфер

    selected_text = pyperclip.paste()

    if not selected_text:
        print("Текст не выделен или не удалось скопировать.")
        pyperclip.copy(original_clipboard)
        return

    print(f"Оригинальный текст: {selected_text}")
    print("Отправка запроса к ИИ...")

    fixed_text = fix_text(selected_text)

    if fixed_text:
        print(f"Исправленный текст: {fixed_text}")
        # Копируем исправленный текст в буфер обмена
        pyperclip.copy(fixed_text)
        time.sleep(0.1)

        # Имитируем Ctrl+V для вставки текста вместо выделенного
        keyboard.send("ctrl+v")
        time.sleep(0.1)
        print("Текст успешно заменен!")
    else:
        print("Не удалось получить исправленный текст.")
        pyperclip.copy(original_clipboard)

def main():
    print("Проверка доступности Ollama...")
    try:
        requests.get("http://localhost:11434")
    except requests.exceptions.ConnectionError:
        print("ПРЕДУПРЕЖДЕНИЕ: Не удалось подключиться к Ollama. Убедитесь, что Ollama запущена на http://localhost:11434")

    print("=========================================================")
    print("Приложение для исправления текста с помощью ИИ запущено.")
    print("Выделите текст в любом приложении и нажмите Ctrl+G.")
    print(f"Текущая модель: {MODEL_NAME}")
    print("Для выхода нажмите Esc.")
    print("=========================================================")

    # Назначаем горячую клавишу
    keyboard.add_hotkey("ctrl+g", on_hotkey)

    # Ожидаем нажатия Esc для выхода
    keyboard.wait("esc")
    print("\nВыход из приложения.")

if __name__ == "__main__":
    main()
