# 🎤 Voice-to-Voice ИИ Агент

Веб-приложение для голосового чата с ИИ агентом Gemini. Поддерживает real-time общение голос-в-голос с автоматическим определением конца речи.

## ✨ Особенности

- 🎙️ **Голосовой ввод** - Нажмите и удерживайте кнопку для записи
- 🤖 **ИИ Gemini** - Умные и естественные ответы
- 🔊 **Голосовой вывод** - ИИ отвечает голосом
- 🎯 **Voice Activity Detection** - Автоматическое определение конца речи
- 🌐 **WebSocket** - Real-time коммуникация
- 📱 **Адаптивный дизайн** - Работает на всех устройствах
- ⌨️ **Клавиатурные сокращения** - Пробел для записи

## 🚀 Быстрый старт

### 1. Установка зависимостей

**Автоматическая установка (рекомендуется):**
```bash
# Клонируйте репозиторий
git clone https://github.com/IgorBlink/nfacback2.3.git
cd nfacback2.3

# Запустите скрипт установки
python install.py
```

**Ручная установка:**
```bash
# Для Python 3.12+ сначала установите базовые инструменты
pip install --upgrade pip setuptools>=68.0.0 wheel>=0.40.0

# Затем установите основные зависимости
pip install -r requirements.txt

# Если проблемы с некоторыми пакетами:
pip install -r requirements-py312.txt

# Для macOS может потребоваться:
brew install portaudio
pip install pyaudio

# Для Ubuntu/Debian:
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio
```

### 2. Настройка Gemini API

1. Получите API ключ от Google AI Studio: https://makersuite.google.com/app/apikey
2. Создайте файл `.env`:

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте файл .env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Запуск приложения

```bash
# Запуск сервера
python main.py

# Или через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Откройте браузер и перейдите на http://localhost:8000

## 🎯 Как использовать

1. **Разрешите доступ к микрофону** при первом запуске
2. **Нажмите и удерживайте** кнопку микрофона (🎤)
3. **Говорите** ваш вопрос или сообщение
4. **Отпустите кнопку** когда закончите говорить
5. **Дождитесь ответа** ИИ агента

### Альтернативные способы записи:
- **Пробел** - нажмите и удерживайте для записи
- **Мобильные устройства** - touch поддержка

## 🏗️ Архитектура проекта

```
voice-ai-agent/
├── main.py                 # Основное FastAPI приложение
├── config.py              # Конфигурация
├── requirements.txt       # Python зависимости
├── README.md             # Документация
├── .env.example          # Пример переменных окружения
│
├── services/             # Бизнес-логика
│   ├── __init__.py
│   ├── audio_service.py   # Обработка аудио и VAD
│   ├── gemini_service.py  # Интеграция с Gemini API
│   └── speech_service.py  # Speech-to-Text и Text-to-Speech
│
├── utils/                # Утилиты
│   ├── __init__.py
│   └── connection_manager.py  # Управление WebSocket
│
├── templates/            # HTML шаблоны
│   └── index.html        # Главная страница
│
└── static/              # Статические файлы
    └── js/
        └── voice-chat.js  # Frontend JavaScript
```

## ⚙️ Конфигурация

Все настройки можно изменить через переменные окружения:

```bash
# API
GEMINI_API_KEY=your_api_key

# Сервер
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Аудио
SAMPLE_RATE=16000          # Частота дискретизации
FRAME_DURATION=30          # Длительность фрейма (мс)
MAX_SILENCE_FRAMES=30      # Фреймы тишины до остановки

# Логирование
LOG_LEVEL=INFO
```

## 🔧 Технологии

**Backend:**
- FastAPI - Веб-фреймворк
- WebSocket - Real-time коммуникация
- Google Generative AI - ИИ модель Gemini
- SpeechRecognition - Распознавание речи
- gTTS - Синтез речи
- WebRTC VAD - Определение активности голоса
- Pydub - Обработка аудио

**Frontend:**
- Vanilla JavaScript - Без дополнительных фреймворков
- Web Audio API - Анализ звука
- MediaRecorder API - Запись аудио
- WebSocket API - Коммуникация с сервером

## 🐛 Устранение неполадок

### Проблемы с микрофоном
- Убедитесь, что браузер имеет доступ к микрофону
- Проверьте настройки приватности браузера
- Используйте HTTPS в продакшене для доступа к микрофону

### Проблемы с установкой PyAudio
```bash
# macOS
brew install portaudio
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"
pip install pyaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio
```

### Проблемы с Gemini API
- Проверьте корректность API ключа
- Убедитесь, что у вас есть доступ к Gemini API
- Проверьте лимиты использования API

## 📝 API Endpoints

- `GET /` - Главная страница
- `WebSocket /ws` - WebSocket для голосового чата

### WebSocket сообщения

**Клиент → Сервер:**
```json
{
  "type": "audio_chunk",
  "data": "base64_audio_data"
}

{
  "type": "audio_end"
}

{
  "type": "clear_history"
}
```

**Сервер → Клиент:**
```json
{
  "type": "connection_established",
  "session_id": "12345678"
}

{
  "type": "transcription",
  "text": "Распознанный текст"
}

{
  "type": "ai_response",
  "text": "Ответ ИИ"
}

{
  "type": "audio_response",
  "data": "base64_audio_data"
}
```

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект использует MIT лицензию.

## 🙏 Благодарности

- Google AI за предоставление Gemini API
- WebRTC за Voice Activity Detection
- FastAPI за отличный веб-фреймворк 