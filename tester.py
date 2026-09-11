import sys
import os
import time

print("="*50)
print("  AI Text Corrector - Diagnostic Tester")
print("="*50)
print("\nПроверка зависимостей...")

try:
    import pyperclip
    import keyboard
    import requests
    import customtkinter
    print("[OK] Все основные библиотеки установлены.")
except ImportError as e:
    print(f"[ERROR] Ошибка импорта: {e}")
    print("Пожалуйста, убедитесь, что вы запустили install.bat")
    sys.exit(1)

# Import our internal modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.config import config_manager
from src.ai_client import ai_client

print("\n[1/3] Проверка буфера обмена (Clipboard)...")
try:
    original = pyperclip.paste()
    test_string = "diagnostic_test_123"
    pyperclip.copy(test_string)
    result = pyperclip.paste()
    if result == test_string:
        print("[OK] Чтение и запись буфера обмена работают исправно.")
    else:
        print("[ERROR] Не удалось записать/прочитать из буфера обмена.")
    pyperclip.copy(original) # Restore
except Exception as e:
    print(f"[ERROR] Ошибка работы с буфером обмена: {e}")


print("\n[2/3] Проверка горячих клавиш (Keyboard Hooks)...")
test_hotkey = "ctrl+alt+shift+t"
try:
    def hook_test(): pass
    keyboard.add_hotkey(test_hotkey, hook_test)
    keyboard.remove_hotkey(hook_test)
    print(f"[OK] Библиотека keyboard успешно регистрирует системные хуки на Windows.")
except Exception as e:
    print(f"[ERROR] Не удалось зарегистрировать горячую клавишу. Запустите программу от имени Администратора. Ошибка: {e}")


print("\n[3/3] Проверка связи с ИИ сервером...")
backend = config_manager.get("backend")
print(f"Текущий выбранный бэкенд: {backend}")

success, msg = ai_client.test_connection(timeout_sec=600)
if success:
    print(f"[OK] Базовое подключение к серверу ({backend}) установлено.")

    print("\n[Extra] Отправка тестового запроса (Full prompt test)...")
    test_text = "тестовое сообщение с ашипкой"
    print(f"Отправляем текст: '{test_text}'")

    start_time = time.time()
    response = ai_client.fix_text(test_text, timeout_sec=600)
    end_time = time.time()

    if response:
        print(f"[OK] ИИ успешно вернул ответ за {round(end_time - start_time, 2)} сек!")
        print(f"Ответ ИИ: '{response}'")
    else:
        print(f"[ERROR] ИИ сервер не вернул ответ. Возможно модель не загружена или возвращает пустую строку (проверьте логи LM Studio).")

else:
    print(f"[ERROR] Ошибка подключения: {msg}")
    print("Убедитесь, что сервер Ollama или LM Studio запущен и порты открыты.")


print("\n" + "="*50)
print("Диагностика завершена. Подробные логи можно найти в файле logs/app.log")
print("="*50)
input("Нажмите Enter для выхода...")
