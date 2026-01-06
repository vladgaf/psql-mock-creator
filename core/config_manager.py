import os
import json
import sys
from peewee import PostgresqlDatabase


def get_base_dir():
    """Получить базовую директорию, работающую в PyInstaller и при разработке"""
    if getattr(sys, 'frozen', False):
        # В PyInstaller: исполняемый файл в sys.executable
        if hasattr(sys, '_MEIPASS'):
            # Во время исполнения файлы во временной папке _MEIPASS
            base_dir = sys._MEIPASS
        else:
            # Если нет _MEIPASS, берём директорию исполняемого файла
            base_dir = os.path.dirname(sys.executable)
    else:
        # При разработке: на один уровень выше core/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return base_dir


# Используем новую функцию
BASE_DIR = get_base_dir()

CONFIG_DIR = os.path.join(BASE_DIR, 'config')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MOCK_DATA_DIR = os.path.join(BASE_DIR, 'mock_data')
POSTGRES_CONFIG_PATH = os.path.join(CONFIG_DIR, 'postgres.json')

# Глобальная переменная для хранения конфигурации
_POSTGRES_CONFIG = None

# Конфигурация баз данных (постоянная)
DATABASES_CONFIG = {
    'games_easy': {
        'db_name': 'games_easy',
        'description': 'База данных видеоигр (простая)',
        'models_module': 'models.games_easy',
        'mock_data_folder': 'games_easy'
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
    },
    'air_travel': {
        'db_name': 'air_travel',
        'description': 'База данных авиа перелетов',
        'models_module': 'models.air_travel',
        'mock_data_folder': 'air_travel'
    }
}


def get_postgres_config():
    """Получает настройки PostgresSQL (загружает при первом вызове)"""
    global _POSTGRES_CONFIG

    if _POSTGRES_CONFIG is None:
        _POSTGRES_CONFIG = _load_postgres_config()

    return _POSTGRES_CONFIG


def _load_postgres_config():
    """Загружает настройки PostgreSQL из JSON файла"""
    try:
        if not os.path.exists(POSTGRES_CONFIG_PATH):
            print(f"⚠️ Файл конфигурации не найден: {POSTGRES_CONFIG_PATH}")
            print("🔄 Используются настройки по умолчанию")
            return _get_default_config()

        with open(POSTGRES_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Проверяем обязательные поля
        required_fields = ['user', 'password', 'host', 'port']
        for field in required_fields:
            if field not in config:
                print(f"⚠️ Отсутствует поле '{field}' в конфигурации")
                return _get_default_config()

        print(f"✅ Конфигурация загружена из {POSTGRES_CONFIG_PATH}")
        return config

    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return _get_default_config()


def save_postgres_config(config_data):
    """Сохраняет настройки PostgreSQL в JSON файл"""
    global _POSTGRES_CONFIG

    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)

        with open(POSTGRES_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

        # Обновляем кэш
        _POSTGRES_CONFIG = config_data

        print(f"✅ Конфигурация сохранена в {POSTGRES_CONFIG_PATH}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения конфигурации: {e}")
        return False


def _get_default_config():
    """Возвращает настройки по умолчанию"""
    return {
        'user': 'postgres',
        'password': '',
        'host': 'localhost',
        'port': 5432
    }


def create_database_connection(db_name, config=None):
    """
    Создает подключение к конкретной базе данных PostgreSQL

    Args:
        db_name: Имя базы данных
        config: Опционально - конфигурация подключения.
                Если не указана, будет загружена автоматически.
    """
    if config is None:
        config = get_postgres_config()

    return PostgresqlDatabase(
        db_name,
        user=config.get('user', 'postgres'),
        password=config.get('password', ''),
        host=config.get('host', 'localhost'),
        port=config.get('port', 5432)
    )


def test_connection(config=None):
    """Тестирует подключение к PostgreSQL"""
    if config is None:
        config = get_postgres_config()

    try:
        conn = create_database_connection('postgres', config)
        conn.connect()
        conn.close()
        print("✅ Подключение к PostgreSQL успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False


def show_postgres_config(config=None):
    """Показывает текущие настройки подключения (без пароля)"""
    if config is None:
        config = get_postgres_config()

    safe_config = config.copy()
    safe_config['password'] = '***' if safe_config.get('password') else ''

    print("📋 Текущие настройки PostgreSQL:")
    for key, value in safe_config.items():
        print(f"   {key}: {value}")
    return safe_config
