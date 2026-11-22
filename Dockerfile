# =============================================================================
# Dockerfile для веб-приложения (Django Admin Panel)
# =============================================================================

# Базовый образ с Python 3.11
FROM python:3.11-slim

# Переменные окружения для Python
# PYTHONDONTWRITEBYTECODE — не создавать .pyc файлы
# PYTHONUNBUFFERED — выводить логи сразу (без буферизации)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория в контейнере
WORKDIR /app

# Копирование файлов зависимостей (оптимизация кэша Docker)
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Проверка здоровья контейнера (каждые 30 секунд)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python manage.py check --fail-level=WARNING || exit 1

# Команда запуска Django-сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
