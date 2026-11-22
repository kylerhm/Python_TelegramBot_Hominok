<<<<<<< HEAD
# Python_TelegramBot_Hominok
Проект: Telegram-бот с функцией календаря

Максим Хоминок

kylerhm

maxim@hominok.ru
=======
# Telegram-бот для управления событиями и встречами

**Учебный проект** — Telegram-бот с функцией календаря, созданный в рамках обучения.

## 👩‍💻 Автор

- **Имя:** Хоминок Максим
- **GitHub:** [kylerhm](https://github.com/kylerhm)
- **Email:** maxim@hominok.ru

## 📋 Описание проекта

Telegram-бот для планирования событий и встреч с интеграцией Django Admin Panel. Позволяет пользователям создавать, редактировать, удалять события, отслеживать статистику и приглашать других пользователей на встречи.

## ✨ Возможности

- 👤 **Регистрация и авторизация** пользователей
- 📅 **Календарь событий** с группировкой по датам
- ➕ **Создание/редактирование/удаление** событий
- 📊 **Статистика** использования бота
- 🤝 **Система встреч** с приглашениями и подтверждением
- 🌍 **Публичные события** других пользователей
- 📤 **Экспорт** событий в CSV и JSON
- 🎨 **Интерактивное меню** с кнопками для быстрого доступа к функциям

## 🛠 Технологии

- **Python** 3.11+
- **python-telegram-bot** v13.15
- **Django** 4.2
- **PostgreSQL** 14
- **Docker** & **Docker Compose**
- **DRF** (Django Rest Framework)

## 📁 Структура проекта

```
├── admin_panel/          # Django приложение
│   ├── events/           # Модель событий, пользователей, встреч
│   └── admin_panel/      # Настройки Django
├── handlers/             # Обработчики команд и callback-кнопок
│   ├── commands.py       # Обработчики команд (/start, /create_event и т.д.)
│   ├── callbacks.py      # Callback-обработчики (меню, публичность)
│   └── meetings.py       # Обработчики встреч
├── utils/                # Вспомогательные функции
│   ├── decorators.py     # Декораторы (@require_registration, @handle_errors)
│   ├── formatters.py     # Форматтеры событий
│   └── parsers.py        # Парсеры входных данных
├── services.py           # Бизнес-логика (пользователи, контексты, встречи)
├── models.py             # Класс Calendar (CRUD-операции)
├── config.py             # Конфигурация (переменные окружения)
├── main.py               # Точка входа бота
├── tests/                # Тесты pytest
├── docker-compose.yml    # Конфигурация Docker
├── Dockerfile            # Образ для веб-приложения
├── Dockerfile.bot        # Образ для бота
├── .env.example          # Шаблон переменных окружения
├── .env.docker           # Переменные для Docker
└── requirements.txt      # Зависимости Python
```

## 🚀 Запуск проекта

### Требования

- Docker и Docker Compose
- Telegram Bot Token (от @BotFather)
- VPN (для подключения бота к Telegram API)

> ⚠️ **Важно:** Бот подключается к Telegram API через VPN. Если бот не запускается, проверьте VPN-соединение.

### Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd part2
   ```

2. Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Заполните переменные окружения в `.env`:
   - `TELEGRAM_BOT_TOKEN` — токен вашего бота
   - `DB_PASSWORD` — пароль для PostgreSQL
   - `SECRET_KEY` — ключ для Django

4. Запустите проект:
   ```bash
   docker-compose up --build
   ```

### Запуск отдельных сервисов

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск только базы данных и веб-приложения
docker-compose up -d db web

# Запуск только бота
docker-compose up -d bot
```

### Остановка

```bash
# Остановка и удаление контейнеров
docker-compose down

# Остановка с удалением volumes (⚠️ удалит данные БД)
docker-compose down -v
```

## 🌐 Доступные сервисы

- **Telegram Bot** — запускается автоматически
- **Django Admin Panel** — http://localhost:8000/admin/
- **API** — http://localhost:8000/events/api/

## 🐳 Docker

### Сборка образов

```bash
# Сборка всех образов
docker-compose build

# Сборка конкретного образа
docker-compose build web
docker-compose build bot
```

### Запуск контейнеров

```bash
# Запуск всех контейнеров в фоне
docker-compose up -d

# Запуск с пересборкой
docker-compose up -d --build

# Запуск с выводом логов
docker-compose up
```

### Управление контейнерами

```bash
# Просмотр запущенных контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs
docker-compose logs -f web    # Логи веб-приложения
docker-compose logs -f bot    # Логи бота

# Перезапуск
docker-compose restart

# Остановка
docker-compose stop

# Удаление контейнеров
docker-compose down
```

### Volume для базы данных

Данные PostgreSQL сохраняются в volume `db_data`. При перезапуске контейнеров данные не теряются:

```bash
# Проверка volume
docker volume ls | grep db_data

# Очистка volume (⚠️ удалит все данные)
docker volume rm part2_db_data
```

## 🧪 Тесты

```bash
# Запуск тестов через Docker
docker-compose exec web python -m pytest tests/ -v

# Запуск тестов локально
pytest tests/ -v
```

## ⚠️ Важно

Это **учебный проект**, созданный для демонстрации навыков работы с:
- Telegram Bot API
- Django ORM и Admin Panel
- Docker контейнеризацией
- PostgreSQL базой данных

Не используйте в продакшене без доработки безопасности!

## 📄 Лицензия

Учебный проект.
>>>>>>> cd6d927 (feat: Telegram-бот для управления событиями и встречами)
