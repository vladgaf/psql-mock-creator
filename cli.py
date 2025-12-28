#!/usr/bin/env python
"""
Консольная версия PSQL Mock Creator
"""

import argparse
from core.database_manager import DatabaseManager
from core.config_manager import get_postgres_config, DATABASES_CONFIG, show_postgres_config


def main():
    parser = argparse.ArgumentParser(
        description='Создание учебных баз данных PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Примеры использования:
              python cli.py --create                      # Создать все базы
              python cli.py --create games_easy school    # Создать указанные базы
              python cli.py --clean                       # Очистить все базы
              python cli.py --list                        # Показать список баз
              python cli.py --config                      # Показать текущий конфиг
        """
    )

    parser.add_argument('--create', nargs='*', metavar='DB_NAME',
                        help='Создать указанные базы данных (или все, если не указано)')
    parser.add_argument('--clean', nargs='*', metavar='DB_NAME',
                        help='Очистить указанные базы данных (или все, если не указано)')
    parser.add_argument('--list', action='store_true',
                        help='Показать список доступных баз данных')
    parser.add_argument('--config', action='store_true',
                        help='Показать текущую конфигурацию PostgreSQL')

    args = parser.parse_args()

    if args.list:
        print("📋 Доступные базы данных:")
        for name, details in DATABASES_CONFIG.items():
            print(f"  • {name}: {details['description']}")
        print(f"\nВсего: {len(DATABASES_CONFIG)} баз данных")
        return

    # Загружаем конфигурацию
    config = get_postgres_config()

    if args.config:
        show_postgres_config(config)
        return

    db_manager = DatabaseManager(config)

    if args.create is not None:
        if len(args.create) == 0:
            # Создать все базы
            print("🚀 Создание всех баз данных...")
            db_manager.create_all_databases()
        else:
            # Создать только указанные
            print(f"🚀 Создание выбранных баз данных: {', '.join(args.create)}")
            db_manager.create_databases(args.create)

    elif args.clean is not None:
        if len(args.clean) == 0:
            # Очистить все базы
            print("🧹 Очистка всех баз данных...")
            db_manager.clean_databases(list(DATABASES_CONFIG.keys()))
        else:
            # Очистить только указанные
            print(f"🧹 Очистка выбранных баз данных: {', '.join(args.clean)}")
            db_manager.clean_databases(args.clean)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
