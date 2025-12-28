from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QPushButton, QCheckBox, QTextEdit, QLabel,
    QLineEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QTextCursor

from core.config_manager import get_postgres_config, save_postgres_config
from core.database_manager import DatabaseManager
from core.logger import OutputLogger
from ui.styles import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = OutputLogger()  # Наш перехватчик print()
        self.setup_ui()
        self.load_saved_config()
        self.setup_console_updater()

    def setup_ui(self):
        """Создает все элементы интерфейса."""
        self.setWindowTitle("PSQL Mock Creator")
        self.setGeometry(100, 100, 900, 700)  # x, y, width, height

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ===== 1. СЕКЦИЯ: Текстовые поля для конфига =====
        config_group = QGroupBox("Настройки подключения к PostgreSQL")
        config_layout = QGridLayout()

        # Создаем поля ввода
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Добавляем поля с подписями
        config_layout.addWidget(QLabel("Хост:"), 0, 0)
        config_layout.addWidget(self.host_input, 0, 1)
        config_layout.addWidget(QLabel("Порт:"), 1, 0)
        config_layout.addWidget(self.port_input, 1, 1)
        config_layout.addWidget(QLabel("Пользователь:"), 2, 0)
        config_layout.addWidget(self.user_input, 2, 1)
        config_layout.addWidget(QLabel("Пароль:"), 3, 0)
        config_layout.addWidget(self.password_input, 3, 1)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # ===== 2. СЕКЦИЯ: Чекбоксы для выбора баз =====
        db_group = QGroupBox("Выберите базы данных для создания")
        db_layout = QGridLayout()

        # Создаем чекбоксы для каждой БД
        self.db_checkboxes = {}
        databases = [
            ("games_easy", "🎮 Простая база видеоигр (1 таблица)"),
            ("school_world", "🏫 Школьная база данных (5 таблиц)"),
            ("games_shop", "🛒 Магазин видеоигр (4 таблицы)"),
            ("air_travel", "✈️ Авиакомпании и перелеты (5 таблиц)")
        ]

        for i, (db_id, db_label) in enumerate(databases):
            checkbox = QCheckBox(db_label)
            checkbox.setChecked(True)  # По умолчанию выбраны
            self.db_checkboxes[db_id] = checkbox
            # Располагаем в 2 колонки
            db_layout.addWidget(checkbox, i // 2, i % 2)

        db_group.setLayout(db_layout)
        main_layout.addWidget(db_group)

        # ===== 3. СЕКЦИЯ: Кнопки управления =====
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)

        # Кнопка "Создать базы данных"
        self.create_btn = QPushButton("🗄️ Создать базы данных")
        self.create_btn.clicked.connect(self.create_databases)
        self.create_btn.setObjectName("createButton")  # Для стилей CSS

        # Кнопка "Очистить базы данных"
        self.clean_btn = QPushButton("🧹 Очистить базы данных")
        self.clean_btn.clicked.connect(self.clean_databases)
        self.clean_btn.setObjectName("cleanButton")

        # Кнопка "Сохранить конфиг"
        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.clicked.connect(self.save_current_config)
        self.save_btn.setObjectName("saveButton")

        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.clean_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()

        main_layout.addWidget(button_frame)

        # ===== 4. СЕКЦИЯ: Окно консоли =====
        console_group = QGroupBox("Консоль вывода")
        console_layout = QVBoxLayout()

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)  # Только для чтения
        self.console_output.setFont(QFont("Courier New", 10))

        # Кнопка очистки консоли
        clear_btn = QPushButton("Очистить консоль")
        clear_btn.clicked.connect(self.clear_console)

        console_layout.addWidget(clear_btn)
        console_layout.addWidget(self.console_output)
        console_group.setLayout(console_layout)

        main_layout.addWidget(console_group, 1)  # 1 = растягиваем

        # Применяем CSS-стили
        self.setStyleSheet(APP_STYLESHEET)

        # Статус бар внизу окна
        self.statusBar().showMessage("Готово")

    def load_saved_config(self):
        """Загружает сохраненный конфиг в поля ввода."""
        config = get_postgres_config()
        self.host_input.setText(config.get('host', 'localhost'))
        self.port_input.setText(str(config.get('port', 5432)))
        self.user_input.setText(config.get('user', 'postgres'))
        self.password_input.setText(config.get('password', ''))

    def get_current_config(self):
        """Возвращает текущие настройки из полей ввода как словарь."""
        return {
            'host': self.host_input.text().strip(),
            'port': int(self.port_input.text()) if self.port_input.text().isdigit() else 5432,
            'user': self.user_input.text().strip(),
            'password': self.password_input.text()
        }

    def get_selected_databases(self):
        """Возвращает список ID выбранных баз данных."""
        selected = []
        for db_id, checkbox in self.db_checkboxes.items():
            if checkbox.isChecked():
                selected.append(db_id)
        return selected

    def save_current_config(self):
        """Сохраняет текущие настройки в файл."""
        config = self.get_current_config()
        save_postgres_config(config)
        self.log_to_console("[INFO] Настройки сохранены в config/postgres.json\n")
        self.statusBar().showMessage("Настройки сохранены", 3000)

    def create_databases(self):
        """Обработчик кнопки 'Создать базы данных'."""
        selected = self.get_selected_databases()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы одну базу данных!")
            return

        config = self.get_current_config()
        self.run_database_operation("create", selected, config)

    def clean_databases(self):
        """Обработчик кнопки 'Очистить базы данных'."""
        selected = self.get_selected_databases()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы одну базу данных!")
            return

        # Запрашиваем подтверждение
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f'Вы уверены, что хотите очистить {len(selected)} баз данных?\nЭто действие удалит все данные.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            config = self.get_current_config()
            self.run_database_operation("clean", selected, config)

    def run_database_operation(self, operation, databases, config):
        """Запускает операцию с БД в отдельном потоке."""
        # Блокируем кнопки на время выполнения
        self.set_buttons_enabled(False)

        # Начинаем перехват print()
        self.logger.start_logging()

        # Запускаем в отдельном потоке, чтобы UI не зависал
        import threading
        def worker():
            try:
                db_manager = DatabaseManager(config)
                if operation == "create":
                    db_manager.create_databases(databases)
                else:
                    db_manager.clean_databases(databases)
            except Exception as e:
                print(f"[ERROR] Ошибка: {e}")
            finally:
                # Восстанавливаем stdout
                self.logger.stop_logging()
                # Разблокируем кнопки в основном потоке UI
                self.set_buttons_enabled(True)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        # Показываем сообщение о начале
        op_name = "создания" if operation == "create" else "очистки"
        self.log_to_console(f"\n{'=' * 60}\n")
        self.log_to_console(f"Запуск {op_name} баз данных: {', '.join(databases)}\n")
        self.log_to_console(f"{'=' * 60}\n\n")
        self.statusBar().showMessage(f"Выполняется {op_name}...")

    def set_buttons_enabled(self, enabled):
        """Блокирует или разблокирует кнопки управления."""
        self.create_btn.setEnabled(enabled)
        self.clean_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)

    def setup_console_updater(self):
        """Настраивает таймер для обновления консоли."""
        self.console_timer = QTimer()
        self.console_timer.timeout.connect(self.update_console_display)
        self.console_timer.start(100)  # Обновлять каждые 100 мс

    def update_console_display(self):
        """Берет накопленные логи из OutputLogger и выводит в QTextEdit."""
        logs = self.logger.get_logs()
        if logs:
            self.console_output.moveCursor(QTextCursor.MoveOperation.End)
            self.console_output.insertPlainText(logs)
            # Автопрокрутка вниз
            self.console_output.ensureCursorVisible()

    def log_to_console(self, message):
        """Прямой вывод сообщения в консоль (для UI событий)."""
        self.console_output.moveCursor(QTextCursor.MoveOperation.End)
        self.console_output.insertPlainText(message)
        self.console_output.ensureCursorVisible()

    def clear_console(self):
        """Очищает окно консоли."""
        self.console_output.clear()
        self.log_to_console(f"[{datetime.now().strftime('%H:%M:%S')}] Консоль очищена\n")