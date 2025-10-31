import os
import json
from peewee import PostgresqlDatabase

# Базовая директория
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к папкам
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MOCK_DATA_DIR = os.path.join(BASE_DIR, 'mock_data')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
UTILS_DIR = os.path.join(BASE_DIR, 'utils')

# Путь к файлу с настройками PostgreSQL
POSTGRES_CONFIG_PATH = os.path.join(CONFIG_DIR, 'postgres.json')


def load_postgres_config():
    """Загружает настройки PostgreSQL из JSON файла"""
    try:
        if not os.path.exists(POSTGRES_CONFIG_PATH):
            raise FileNotFoundError(f"Файл конфигурации не найден: {POSTGRES_CONFIG_PATH}")

        with open(POSTGRES_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Проверяем обязательные поля
        required_fields = ['user', 'password', 'host', 'port']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Отсутствует обязательное поле '{field}' в конфигурации")

        print(f"✅ Конфигурация PostgreSQL загружена из {POSTGRES_CONFIG_PATH}")
        return config

    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации PostgreSQL: {e}")
        print("🔄 Используются настройки по умолчанию")

        # Настройки по умолчанию
        return {
            'user': 'postgres',
            'password': '0000',
            'host': 'localhost',
            'port': 5432
        }


# Загружаем настройки PostgreSQL
POSTGRES_CONFIG = load_postgres_config()

# Список баз данных для создания
DATABASES_CONFIG = {
    'video_games': {
        'db_name': 'games_easy',
        'description': 'База данных видеоигр (простая)',
        'models_module': 'models.video_games',
        'mock_data_folder': 'video_games'
    },
    'school_world': {
        'db_name': 'school_world',
        'description': 'Школьная база данных',
        'models_module': 'models.school_world',
        'mock_data_folder': 'school_world'
    },
    'games_shop': {
        'db_name': 'games_shop',
        'description': 'Магазин видеоигр с заказами',
        'models_module': 'models.games_shop',
        'mock_data_folder': 'games_shop'
    }
}


def create_database_connection(db_name):
    """Создает подключение к конкретной базе данных PostgreSQL"""
    return PostgresqlDatabase(
        db_name,
        user=POSTGRES_CONFIG['user'],
        password=POSTGRES_CONFIG['password'],
        host=POSTGRES_CONFIG['host'],
        port=POSTGRES_CONFIG['port']
    )


def test_connection():
    """Тестирует подключение к PostgreSQL"""
    try:
        conn = create_database_connection('postgres')
        conn.connect()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False


def show_postgres_config():
    """Показывает текущие настройки подключения (без пароля)"""
    safe_config = POSTGRES_CONFIG.copy()
    safe_config['password'] = '***'  # Скрываем пароль для безопасности
    print("📋 Текущие настройки PostgreSQL:")
    for key, value in safe_config.items():
        print(f"   {key}: {value}")