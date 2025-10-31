#!/usr/bin/env python3
"""
Скрипт для очистки учебных баз данных
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import POSTGRES_CONFIG, DATABASES_CONFIG


def cleanup_databases():
    """Удаляет все учебные базы данных"""
    print("🧹 ОЧИСТКА УЧЕБНЫХ БАЗ ДАННЫХ")
    print("=" * 40)

    try:
        # Подключаемся к postgres для удаления баз
        conn = psycopg2.connect(
            user=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password'],
            host=POSTGRES_CONFIG['host'],
            port=POSTGRES_CONFIG['port'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        for db_name, db_config in DATABASES_CONFIG.items():
            try:
                # Проверяем существование базы
                cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_config['db_name'],))
                exists = cursor.fetchone()

                if exists:
                    # Завершаем все соединения с базой
                    cursor.execute(f"""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = '{db_config['db_name']}'
                        AND pid <> pg_backend_pid();
                    """)

                    # Удаляем базу
                    cursor.execute(f'DROP DATABASE "{db_config["db_name"]}"')
                    print(f"✅ База '{db_config['db_name']}' удалена")
                else:
                    print(f"ℹ️ База '{db_config['db_name']}' не существует")

            except Exception as e:
                print(f"❌ Ошибка при удалении базы '{db_config['db_name']}': {e}")

        cursor.close()
        conn.close()
        print("\n🎯 Очистка завершена!")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")


if __name__ == "__main__":
    cleanup_databases()