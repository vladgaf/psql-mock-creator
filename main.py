#!/usr/bin/env python3
"""
Главный скрипт для создания всех учебных баз данных PostgreSQL
"""

from database_manager import DatabaseManager
from config import test_connection, show_postgres_config


def main():
    """Основная функция создания всех баз данных"""
    print("🚀 СИСТЕМА СОЗДАНИЯ УЧЕБНЫХ БАЗ ДАННЫХ PostgreSQL")
    print("=" * 50)

    # Показываем текущую конфигурацию
    show_postgres_config()
    print("=" * 50)

    # Проверяем подключение к PostgreSQL
    if not test_connection():
        print("❌ Не удалось подключиться к PostgreSQL")
        print("🔧 Проверьте:")
        print("   - Запущен ли PostgreSQL сервер")
        print("   - Правильность настроек в config/postgres.json")
        print("   - Наличие прав у пользователя postgres")
        return

    try:
        # Создаем менеджер и запускаем создание всех БД
        manager = DatabaseManager()
        manager.create_all_databases()

        print(f"\n🎯 Создание завершено!")
        print("💡 Теперь можно изучать SQL с различными базами данных PostgreSQL!")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("💡 Совет: Попробуйте удалить существующие базы данных и запустить скрипт заново")


if __name__ == "__main__":
    main()