#!/usr/bin/env python3
"""
Скрипт установки Voice-to-Voice ИИ Агента с решением проблем Python 3.12+
"""

import sys
import subprocess
import platform
import os

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Проверяет версию Python"""
    version = sys.version_info
    print(f"🐍 Python версия: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    
    return True

def install_base_tools():
    """Устанавливает базовые инструменты"""
    print("🔧 Установка базовых инструментов...")
    
    commands = [
        "pip install --upgrade pip",
        "pip install --upgrade setuptools>=68.0.0",
        "pip install --upgrade wheel>=0.40.0"
    ]
    
    for cmd in commands:
        print(f"  Выполняю: {cmd}")
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"  ⚠️  Предупреждение: {cmd} завершилась с ошибкой")
            print(f"     {stderr}")
    
    print("✅ Базовые инструменты установлены")

def install_main_dependencies():
    """Устанавливает основные зависимости"""
    print("📦 Установка основных зависимостей...")
    
    # Основные пакеты без проблемных
    safe_packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "websockets==12.0",
        "google-generativeai==0.3.2",
        "speechrecognition==3.10.0",
        "pydub==0.25.1",
        "gtts==2.4.0",
        "numpy==1.24.3",
        "python-multipart==0.0.6",
        "jinja2==3.1.2",
        "aiofiles==23.2.1",
        "python-socketio==5.10.0"
    ]
    
    for package in safe_packages:
        print(f"  Устанавливаю: {package}")
        success, stdout, stderr = run_command(f"pip install {package}")
        if not success:
            print(f"  ❌ Ошибка установки {package}: {stderr}")
            return False
    
    print("✅ Основные зависимости установлены")
    return True

def install_problematic_packages():
    """Устанавливает проблемные пакеты с альтернативами"""
    print("⚠️  Установка проблемных пакетов...")
    
    # Пытаемся установить webrtcvad
    print("  Попытка установки webrtcvad...")
    success, stdout, stderr = run_command("pip install webrtcvad==2.0.10")
    if not success:
        print("  ❌ webrtcvad не установлен (это не критично)")
        print("     VAD будет работать в упрощенном режиме")
    else:
        print("  ✅ webrtcvad установлен")
    
    # Пытаемся установить pyaudio
    print("  Попытка установки PyAudio...")
    
    system = platform.system().lower()
    if system == "darwin":  # macOS
        print("    Система: macOS")
        print("    Попробуйте: brew install portaudio")
        run_command("brew install portaudio")
    elif system == "linux":  # Linux
        print("    Система: Linux")
        print("    Попробуйте: sudo apt-get install portaudio19-dev")
    
    success, stdout, stderr = run_command("pip install pyaudio==0.2.11")
    if not success:
        print("  ❌ PyAudio не установлен")
        print("     Микрофон может не работать")
        print("     Попробуйте установить вручную или используйте веб-интерфейс")
    else:
        print("  ✅ PyAudio установлен")

def create_env_file():
    """Создает файл окружения"""
    print("📝 Создание файла .env...")
    
    if not os.path.exists(".env"):
        if os.path.exists("env_example.txt"):
            run_command("cp env_example.txt .env")
            print("✅ Файл .env создан из примера")
            print("🔑 НЕ ЗАБУДЬТЕ добавить ваш GEMINI_API_KEY в файл .env!")
        else:
            with open(".env", "w") as f:
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
                f.write("DEBUG=True\n")
            print("✅ Файл .env создан")
            print("🔑 НЕ ЗАБУДЬТЕ добавить ваш GEMINI_API_KEY в файл .env!")
    else:
        print("ℹ️  Файл .env уже существует")

def main():
    """Основная функция установки"""
    print("🚀 Установка Voice-to-Voice ИИ Агента")
    print("=" * 50)
    
    if not check_python_version():
        sys.exit(1)
    
    install_base_tools()
    
    if not install_main_dependencies():
        print("❌ Ошибка установки основных зависимостей")
        sys.exit(1)
    
    install_problematic_packages()
    create_env_file()
    
    print("\n🎉 Установка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Получите API ключ Gemini: https://aistudio.google.com/app/apikey")
    print("2. Добавьте ключ в файл .env: GEMINI_API_KEY=ваш_ключ")
    print("3. Запустите: python start.py")
    print("\n💡 При проблемах смотрите README.md")

if __name__ == "__main__":
    main() 