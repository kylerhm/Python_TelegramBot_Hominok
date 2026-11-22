"""
Конфигурация бота: переменные окружения, настройки Django и БД.
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# --- Telegram API Token ---
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN! Проверьте файл .env")

# --- Database settings ---
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    missing = [k for k, v in
               {'DB_HOST': DB_HOST, 'DB_NAME': DB_NAME, 'DB_USER': DB_USER, 'DB_PASSWORD': DB_PASSWORD}.items() if
               not v]
    raise RuntimeError(f"Не заданы переменные окружения для БД: {', '.join(missing)}. Проверьте .env")

# --- Django setup ---
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, 'admin_panel'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_panel.settings")

import django
django.setup()

# Override Django DB settings for local run (only if not in Docker)
import os
if os.environ.get('DB_HOST') == 'localhost':
    from django.conf import settings
    settings.DATABASES['default']['HOST'] = '127.0.0.1'
    settings.DATABASES['default']['PORT'] = str(DB_PORT)

# --- Export API URL ---
EXPORT_API_URL = os.environ.get("EXPORT_API_URL", "http://127.0.0.1:8000/events/export/")
