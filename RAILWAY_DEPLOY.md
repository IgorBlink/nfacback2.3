# 🚀 Деплой на Railway

Простая инструкция по развертыванию Voice-to-Voice ИИ агента на Railway.

## 📋 Что нужно

1. Аккаунт на [Railway](https://railway.app)
2. API ключ Gemini от [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Этот репозиторий на GitHub

## 🚀 Шаги деплоя

### 1. Подключите репозиторий к Railway

1. Заходите на [Railway.app](https://railway.app)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите репозиторий `nfacback2.3`

### 2. Настройте переменные окружения

В Railway dashboard добавьте переменные:

```
GEMINI_API_KEY=ваш_реальный_ключ_gemini
HOST=0.0.0.0
DEBUG=False
LOG_LEVEL=INFO
SAMPLE_RATE=16000
FRAME_DURATION=30
MAX_SILENCE_FRAMES=30
```

### 3. Деплой запустится автоматически

Railway автоматически:
- Обнаружит `Dockerfile`
- Соберет контейнер
- Запустит приложение
- Даст вам URL

## 🎯 После деплоя

1. Откройте предоставленный URL
2. Разрешите доступ к микрофону
3. Начинайте общаться с ИИ!

## 🔧 Настройки для Railway

Проект уже настроен для Railway:

- ✅ **Dockerfile** - оптимизирован для контейнера
- ✅ **railway.toml** - конфигурация Railway
- ✅ **requirements-prod.txt** - стабильные зависимости
- ✅ **PORT** - читается из переменных окружения
- ✅ **Логирование** - настроено для продакшена

## 🐛 Если что-то не работает

1. Проверьте переменные окружения в Railway
2. Убедитесь что `GEMINI_API_KEY` правильный
3. Посмотрите логи в Railway dashboard
4. Убедитесь что используется HTTPS (для микрофона)

## 💰 Стоимость

Railway предоставляет бесплатный тариф с лимитами:
- 500 часов выполнения в месяц
- 1GB RAM
- 1GB диск

Для большего трафика понадобится платный план.

## 🌟 Готово!

Ваш Voice-to-Voice ИИ агент работает в облаке! 🎉 