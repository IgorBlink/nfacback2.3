#!/usr/bin/env python3
"""
Скрипт запуска Voice-to-Voice ИИ Агента
"""

import os
import sys
import logging
from pathlib import Path

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'websockets',
        'google.generativeai',
        'speech_recognition',
        'gtts',
        'pydub',
        'webrtcvad',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Отсутствуют следующие пакеты:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n🔧 Установите их командой:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def check_config():
    """Проверка конфигурации"""
    from config import config
    
    try:
        config.validate()
        print("✅ Конфигурация корректна")
        return True
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("\n💡 Создайте файл .env из примера:")
        print("cp env_example.txt .env")
        print("Затем отредактируйте .env и добавьте ваш GEMINI_API_KEY")
        return False

def check_directories():
    """Проверка необходимых директорий"""
    directories = ['static/js', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Директории проверены")
    return True

def start_server():
    """Запуск сервера"""
    try:
        import uvicorn
        from config import config
        
        print(f"🚀 Запуск сервера на http://{config.HOST}:{config.PORT}")
        print("📱 Откройте браузер и перейдите по адресу выше")
        print("🎤 Разрешите доступ к микрофону для начала работы")
        print("\n⏹️  Для остановки нажмите Ctrl+C")
        
        uvicorn.run(
            "main:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,
            log_level=config.LOG_LEVEL.lower()
        )
        
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

def main():
    """Основная функция"""
    print("🎤 Voice-to-Voice ИИ Агент")
    print("=" * 50)
    
    setup_logging()
    
    # Проверки перед запуском
    if not check_dependencies():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    check_directories()
    
    # Запуск сервера
    start_server()

if __name__ == "__main__":
    main() 