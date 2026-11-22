"""
Конфигурация pytest: загрузка .env перед инициализацией Django.
"""
import os
import sys
from pathlib import Path

# Загружаем .env до импорта Django
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "admin_panel"))
