# Используем Python 3.11 (3.12 имеет проблемы с distutils в Railway)
FROM python:3.11.7-slim

# Устанавливаем переменную окружения для Python
ENV PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы требований
COPY requirements-prod.txt ./requirements.txt

# Обновляем pip и устанавливаем базовые инструменты
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Устанавливаем setuptools с distutils для Python 3.12+ совместимости
RUN pip install --no-cache-dir 'setuptools[distutils]>=68.0.0'

# Устанавливаем основные зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории если их нет
RUN mkdir -p static/js templates

# Открываем порт
EXPOSE 8000

# Команда запуска (PORT будет установлен Railway автоматически)
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"] 