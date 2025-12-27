import json
import os

CONFIG_PATH = os.path.join('config', 'postgres.json')

def load_config():
    """Загружает конфигурацию из файла."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"user": "postgres", "password": "", "host": "localhost", "port": 5432}

def save_config(config_data):
    """Сохраняет конфигурацию в файл."""
    os.makedirs('config', exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config_data, f, indent=4)