import importlib
import json
import os
import traceback
from datetime import datetime

import psycopg2
from peewee import PostgresqlDatabase
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from core.config_manager import MOCK_DATA_DIR, DATABASES_CONFIG


class DatabaseManager:
    def __init__(self, config):
        """Инициализация с конфигом (словарем)."""
        self.config = config
        self.created_databases = []

        # Используем конфиг для подключения к postgres
        self.db = PostgresqlDatabase(
            'postgres',
            user=self.config.get('user', 'postgres'),
            password=self.config.get('password', ''),
            host=self.config.get('host', 'localhost'),
            port=self.config.get('port', 5432)
        )

    # ==================== ОСНОВНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ ====================

    def create_databases(self, databases_list):
        """Создает несколько выбранных баз данных"""
        print(f"🎓 СОЗДАНИЕ ВЫБРАННЫХ БАЗ ДАННЫХ")
        print("=" * 60)
        print(f"📡 Подключение к: {self.config['host']}:{self.config['port']}")
        print(f"👤 Пользователь: {self.config['user']}")
        print(f"📋 Выбрано баз: {len(databases_list)}")
        print("=" * 60)

        success_count = 0

        for db_name in databases_list:
            if db_name in DATABASES_CONFIG:
                if self._create_single_database(db_name, DATABASES_CONFIG[db_name]):
                    success_count += 1
            else:
                print(f"❌ База данных '{db_name}' не найдена в конфигурации")

        self._show_create_summary(success_count, databases_list)
        return success_count

    def clean_databases(self, databases_list):
        """Очищает выбранные базы данных"""
        print(f"🧹 ОЧИСТКА ВЫБРАННЫХ БАЗ ДАННЫХ")
        print("=" * 60)
        print(f"📋 Выбрано баз для очистки: {len(databases_list)}")
        print("=" * 60)

        success_count = 0

        for db_name in databases_list:
            if db_name in DATABASES_CONFIG:
                if self._clean_single_database(db_name, DATABASES_CONFIG[db_name]):
                    success_count += 1
            else:
                print(f"❌ База данных '{db_name}' не найдена в конфигурации")

        print(f"\n{'=' * 60}")
        print(f"🧹 Очищено баз: {success_count} из {len(databases_list)}")
        print(f"{'=' * 60}\n")

        return success_count

    def create_all_databases(self):
        """Создает все базы данных из конфигурации"""
        print("🎓 ЗАПУСК СОЗДАНИЯ УЧЕБНЫХ БАЗ ДАННЫХ PostgreSQL")
        print("=" * 60)
        print(f"📡 Подключение к: {self.config['host']}:{self.config['port']}")
        print(f"👤 Пользователь: {self.config['user']}")
        print("=" * 60)

        success_count = 0
        for db_name, db_config in DATABASES_CONFIG.items():
            if self._create_single_database(db_name, db_config):
                success_count += 1

        self._show_create_summary(success_count, list(DATABASES_CONFIG.keys()))
        return success_count

    # ==================== МЕТОДЫ СОЗДАНИЯ БАЗ ДАННЫХ ====================

    def _create_single_database(self, db_name, db_config):
        """Создает одну базу данных с таблицами и данными"""
        print(f"\n{'=' * 50}")
        print(f"Создание базы данных: {db_config['description']}")
        print(f"Имя базы: {db_config['db_name']}")
        print(f"{'=' * 50}")

        try:
            # Создаем базу данных если она не существует
            if not self._create_database_if_not_exists(db_config['db_name']):
                return False

            # Импортируем модели для этой БД
            models_module = importlib.import_module(db_config['models_module'])
            database = models_module.get_database()
            models = models_module.get_models()

            # Подключаемся к базе данных
            print("🔗 Подключение к базе данных...")
            database.connect()
            print("✅ Подключение к базе данных установлено")

            # Очищаем и создаем таблицы
            if not self._drop_database_tables(database, models):
                print("⚠️ Продолжаем без очистки таблиц")

            if not self._create_database_tables(database, models):
                print("❌ Не удалось создать таблицы, пропускаем базу")
                database.close()
                return False

            # Загружаем моковые данные
            self._load_mock_data_smart(db_config, models_module, database)

            # Показываем статистику
            self._show_database_stats(models_module)

            # Закрываем соединение
            database.close()
            print("✅ Соединение с базой данных закрыто")

            self.created_databases.append(db_config['db_name'])
            return True

        except Exception as e:
            print(f"❌ Ошибка при создании базы {db_name}: {e}")
            traceback.print_exc()

            # Пытаемся закрыть соединение в случае ошибки
            try:
                if 'database' in locals() and not database.is_closed():
                    database.close()
            except BaseException:
                pass
            return False

    def _create_database_if_not_exists(self, db_name):
        """Создает базу данных PostgreSQL если она не существует"""
        try:
            # Используем self.config вместо POSTGRES_CONFIG
            conn = psycopg2.connect(
                user=self.config.get('user', 'postgres'),
                password=self.config.get('password', ''),
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Проверяем существование базы данных
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"✅ База данных '{db_name}' создана")
            else:
                print(f"ℹ️ База данных '{db_name}' уже существует")

            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Ошибка при создании базы данных '{db_name}': {e}")
            return False

    def _drop_database_tables(self, database, models):
        """Безопасно удаляет таблицы базы данных"""
        try:
            print("🧹 Очистка существующих таблиц...")
            self._drop_all_views(database)
            database.drop_tables(models, safe=False)
            print("✅ Таблицы очищены")
            return True
        except Exception as e:
            print(f"⚠️ Не удалось очистить таблицы: {e}")
            return False

    @staticmethod
    def _create_database_tables(database, models):
        """Безопасно создает таблицы базы данных"""
        try:
            print("📋 Создание таблиц...")
            database.create_tables(models)
            print("✅ Таблицы созданы успешно!")
            return True
        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")
            return False

    @staticmethod
    def _drop_all_views(database):
        """Удаляет все VIEW из базы данных"""
        try:
            with database.connection_context():
                cursor = database.execute_sql("""
                    SELECT table_name 
                    FROM information_schema.views 
                    WHERE table_schema = 'public'
                """)

                views = cursor.fetchall()

                for view in views:
                    view_name = view[0]
                    try:
                        database.execute_sql(f'DROP VIEW IF EXISTS "{view_name}" CASCADE')
                        print(f"  🗑️ Удален VIEW: {view_name}")
                    except Exception as e:
                        print(f"  ⚠️ Не удалось удалить VIEW {view_name}: {e}")

        except Exception as e:
            print(f"⚠️ Ошибка при получении списка VIEW: {e}")
            raise

    # ==================== МЕТОДЫ ОЧИСТКИ БАЗ ДАННЫХ ====================

    def _clean_single_database(self, db_name, db_config):
        """Очищает одну базу данных"""
        print(f"\n{'=' * 50}")
        print(f"Очистка базы данных: {db_config['description']}")
        print(f"Имя базы: {db_config['db_name']}")
        print(f"{'=' * 50}")

        try:
            # Импортируем модели для этой БД
            models_module = importlib.import_module(db_config['models_module'])
            database = models_module.get_database()
            models = models_module.get_models()

            # Подключаемся к базе данных
            print("🔗 Подключение к базе данных...")
            database.connect()
            print("✅ Подключение к базе данных установлено")

            # Очищаем таблицы
            if not self._drop_database_tables(database, models):
                print("⚠️ Не удалось очистить таблицы")
                database.close()
                return False

            print("✅ База данных очищена")
            database.close()
            return True

        except Exception as e:
            print(f"❌ Ошибка при очистке базы {db_name}: {e}")
            traceback.print_exc()
            return False

    # ==================== МЕТОДЫ ЗАГРУЗКИ ДАННЫХ ====================

    def _load_mock_data_smart(self, db_config, models_module, database):
        """Умная загрузка данных с обработкой ошибок для каждой записи"""
        mock_data_path = os.path.join(MOCK_DATA_DIR, db_config['mock_data_folder'])

        if not os.path.exists(mock_data_path):
            print(f"⚠️ Папка с данными не найдена: {mock_data_path}")
            return

        print(f"📂 Загрузка данных из: {db_config['mock_data_folder']}")

        # Определяем порядок загрузки
        loading_order = self._get_loading_order(db_config['db_name'])
        print(f"🔀 Порядок загрузки: {', '.join(loading_order)}")

        # Создаем mapping имен файлов к классам моделей
        model_mapping = {}
        for model in models_module.get_models():
            table_name = getattr(model._meta, 'table_name', model.__name__.lower())
            model_mapping[table_name] = model
            model_mapping[model.__name__.lower()] = model

        # Загружаем данные в правильном порядке
        for table_name in loading_order:
            self._load_table_safely(mock_data_path, table_name, model_mapping, models_module, database)

    @staticmethod
    def _get_loading_order(db_name):
        """Определяет порядок загрузки данных"""
        loading_orders = {
            'school_world': ['teachers', 'classes', 'students', 'subjects', 'grades'],
            'games_easy': ['games', 'reviews'],
            'games_shop': ['games', 'customers', 'orders', 'order_items'],
            'air_travel': ['airlines', 'airports', 'aircrafts', 'flights', 'passengers']
        }
        return loading_orders.get(db_name, [])

    def _load_table_safely(self, mock_data_path, table_name, model_mapping, models_module, database):
        """Безопасно загружает данные для одной таблицы"""
        try:
            filename = f"{table_name}.json"
            file_path = os.path.join(mock_data_path, filename)

            if not os.path.exists(file_path):
                print(f"  ⚠️ Файл {filename} не найден")
                return

            # Ищем модель
            model_class = model_mapping.get(table_name)
            if not model_class:
                class_name = table_name.capitalize()
                model_class = getattr(models_module, class_name, None)

            if not model_class:
                print(f"  ⚠️ Модель для таблицы '{table_name}' не найдена")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not data:
                print(f"  ⚠️ {table_name}: файл пуст")
                return

            print(f"  📖 {table_name}: {len(data)} записей")

            # Обрабатываем даты
            processed_data = self._process_dates(data)

            # Загружаем данные - КАЖДУЮ ЗАПИСЬ В ОТДЕЛЬНОЙ ТРАНЗАКЦИИ
            inserted_count = 0
            errors_count = 0

            for i, item in enumerate(processed_data):
                try:
                    with database.atomic():
                        model_class.create(**item)
                    inserted_count += 1

                except Exception as e:
                    errors_count += 1
                    error_msg = str(e)

                    if 'duplicate key' in error_msg or 'unique constraint' in error_msg:
                        print(f"    ⚠️ Дубликат записи {i + 1}: пропускаем")
                    elif 'foreign key' in error_msg.lower():
                        print(f"    ⚠️ Ошибка внешнего ключа в записи {i + 1}: пропускаем")
                    else:
                        print(f"    ⚠️ Ошибка в записи {i + 1}: {error_msg}")

            # Отчет по таблице
            if errors_count == 0:
                print(f"  ✅ {table_name}: все {inserted_count} записей добавлены")
            else:
                print(f"  ⚠️ {table_name}: {inserted_count} добавлено, {errors_count} ошибок")

        except Exception as e:
            print(f"  ❌ Критическая ошибка загрузки {table_name}: {e}")

    @staticmethod
    def _process_dates(data):
        """Обрабатывает поля с датами в данных"""
        processed_data = []
        for item in data:
            processed_item = item.copy()
            for key, value in item.items():
                if isinstance(value, str) and ('date' in key.lower() or 'birth' in key.lower()):
                    try:
                        processed_item[key] = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        pass
            processed_data.append(processed_item)
        return processed_data

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    @staticmethod
    def _show_database_stats(models_module):
        """Показывает статистику по созданной базе данных"""
        print(f"\n📊 Статистика базы данных:")

        for model in models_module.get_models():
            try:
                count = model.select().count()
                print(f"   {model.__name__}: {count} записей")
            except Exception as e:
                print(f"   {model.__name__}: ошибка при подсчете - {e}")

    def _show_create_summary(self, success_count, databases_list):
        """Показывает итоговую сводку создания"""
        print(f"\n{'=' * 60}")
        print("🎉 ИТОГИ СОЗДАНИЯ БАЗ ДАННЫХ")
        print(f"{'=' * 60}")
        print(f"✅ Успешно создано: {success_count} из {len(databases_list)} баз")
        if self.created_databases:
            print(f"📁 Созданные базы: {', '.join(self.created_databases)}")
            print(f"\n💡 Примеры подключения:")
            for db in self.created_databases:
                print(f"   psql -h {self.config['host']} -U {self.config['user']} -d {db}")
