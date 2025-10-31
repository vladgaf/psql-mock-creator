import json
import os
import importlib
from datetime import datetime
from config import MOCK_DATA_DIR, DATABASES_CONFIG, POSTGRES_CONFIG
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DatabaseManager:
    def __init__(self):
        self.created_databases = []

    def create_database_if_not_exists(self, db_name):
        """Создает базу данных PostgreSQL если она не существует"""
        try:
            # Подключаемся к базе postgres для создания новой БД
            conn = psycopg2.connect(
                user=POSTGRES_CONFIG['user'],
                password=POSTGRES_CONFIG['password'],
                host=POSTGRES_CONFIG['host'],
                port=POSTGRES_CONFIG['port'],
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

    def create_database(self, db_name, db_config):
        """Создает одну базу данных с таблицами и данными"""
        print(f"\n{'=' * 50}")
        print(f"Создание базы данных: {db_config['description']}")
        print(f"Имя базы: {db_config['db_name']}")
        print(f"{'=' * 50}")

        try:
            # Создаем базу данных если она не существует
            if not self.create_database_if_not_exists(db_config['db_name']):
                return False

            # Импортируем модели для этой БД
            models_module = importlib.import_module(db_config['models_module'])
            database = models_module.get_database()
            models = models_module.get_models()

            # Подключаемся к базе данных
            database.connect()
            print("✅ Подключение к базе данных установлено")

            # Очищаем таблицы перед созданием (если они уже существуют)
            database.drop_tables(models, safe=True)

            # Создаем таблицы
            database.create_tables(models)
            print(f"✅ Таблицы созданы успешно!")

            # Загружаем моковые данные
            self._load_mock_data_smart(db_config, models_module, database)

            # Показываем статистику
            self._show_database_stats(models_module, database)

            # Закрываем соединение
            database.close()
            print("✅ Соединение с базой данных закрыто")

            self.created_databases.append(db_config['db_name'])
            return True

        except Exception as e:
            print(f"❌ Ошибка при создании базы {db_name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _get_loading_order(self, db_name, models_module):
        """Определяет порядок загрузки данных"""
        # Для school_world используем фиксированный порядок
        if db_name == 'school_world':
            return ['teachers', 'classes', 'students', 'subjects', 'grades']
        elif db_name == 'games_easy':
            return ['games']
        else:
            # Автоматическое определение для других баз
            models = models_module.get_models()
            model_dependencies = {}

            for model in models:
                dependencies = []
                for field_name, field in model._meta.fields.items():
                    if hasattr(field, 'rel_model') and field.rel_model:
                        dependencies.append(field.rel_model.__name__.lower())
                model_dependencies[model.__name__.lower()] = dependencies

            # Топологическая сортировка
            loading_order = []
            visited = set()

            def visit(model_name):
                if model_name in visited:
                    return
                visited.add(model_name)
                for dependency in model_dependencies.get(model_name, []):
                    visit(dependency)
                loading_order.append(model_name)

            for model_name in model_dependencies.keys():
                visit(model_name)

            return loading_order

    def _load_mock_data_smart(self, db_config, models_module, database):
        """Умная загрузка данных с обработкой ошибок для каждой записи"""
        mock_data_path = os.path.join(MOCK_DATA_DIR, db_config['mock_data_folder'])

        if not os.path.exists(mock_data_path):
            print(f"⚠️ Папка с данными не найдена: {mock_data_path}")
            return

        print(f"📂 Загрузка данных из: {db_config['mock_data_folder']}")

        # Определяем порядок загрузки
        loading_order = self._get_loading_order(db_config['db_name'], models_module)
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
                    # Используем отдельную транзакцию для каждой записи
                    with database.atomic():
                        model_class.create(**item)
                    inserted_count += 1

                except Exception as e:
                    errors_count += 1
                    error_msg = str(e)

                    # Определяем тип ошибки для более информативного сообщения
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

    def _process_dates(self, data):
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

    def _show_database_stats(self, models_module, database):
        """Показывает статистику по созданной базе данных"""
        print(f"\n📊 Статистика базы данных:")

        for model in models_module.get_models():
            try:
                count = model.select().count()
                print(f"   {model.__name__}: {count} записей")
            except Exception as e:
                print(f"   {model.__name__}: ошибка при подсчете - {e}")

    def create_all_databases(self):
        """Создает все базы данных из конфигурации"""
        print("🎓 ЗАПУСК СОЗДАНИЯ УЧЕБНЫХ БАЗ ДАННЫХ PostgreSQL")
        print("=" * 60)
        print(f"📡 Подключение к: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
        print(f"👤 Пользователь: {POSTGRES_CONFIG['user']}")
        print("=" * 60)

        success_count = 0
        for db_name, db_config in DATABASES_CONFIG.items():
            if self.create_database(db_name, db_config):
                success_count += 1

        self._show_summary(success_count)

    def _show_summary(self, success_count):
        """Показывает итоговую сводку"""
        print(f"\n{'=' * 60}")
        print("🎉 ИТОГИ СОЗДАНИЯ БАЗ ДАННЫХ")
        print(f"{'=' * 60}")
        print(f"✅ Успешно создано: {success_count} из {len(DATABASES_CONFIG)} баз")
        print(f"📁 Созданные базы: {', '.join(self.created_databases)}")

        if self.created_databases:
            print(f"\n💡 Примеры подключения:")
            for db in self.created_databases:
                print(f"   psql -h localhost -U postgres -d {db}")