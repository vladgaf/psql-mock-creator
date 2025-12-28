from datetime import datetime
import os
import threading

from PyQt6.QtCore import QTimer, QSettings
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QPushButton, QCheckBox, QTextEdit, QLabel,
    QLineEdit, QMessageBox, QFrame, QStatusBar
)

from core.config_manager import get_postgres_config, save_postgres_config
from core.database_manager import DatabaseManager
from core.logger import OutputLogger
from ui.styles import (
    LIGHT_THEME, DARK_THEME,
    VERSION_WIDGET_STYLE_LIGHT, VERSION_WIDGET_STYLE_DARK,
    CONSOLE_BUTTON_STYLE_LIGHT, CONSOLE_BUTTON_STYLE_DARK,
    DISABLED_BUTTON_STYLE_LIGHT, DISABLED_BUTTON_STYLE_DARK
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = OutputLogger()

        # Загрузка настроек темы
        self.settings = QSettings("PSQLMockCreator", "AppSettings")
        self.current_theme = self.settings.value("theme", "light", type=str)

        self.setup_ui()
        self.setup_status_bar()
        self.load_saved_config()
        self.setup_console_updater()

        # Применяем сохраненную тему
        self.apply_theme(self.current_theme)

    def setup_ui(self):
        """Создает все элементы интерфейса."""
        self.setWindowTitle("PSQL Mock Creator")
        self.setGeometry(100, 100, 900, 700)

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
            checkbox.setChecked(True)
            self.db_checkboxes[db_id] = checkbox
            db_layout.addWidget(checkbox, i // 2, i % 2)

        db_group.setLayout(db_layout)
        main_layout.addWidget(db_group)

        # ===== 3. СЕКЦИЯ: Кнопки управления =====
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 10)

        # Создаем контейнер для центрирования кнопок
        button_container = QWidget()
        button_container_layout = QHBoxLayout(button_container)
        button_container_layout.setSpacing(15)
        button_container_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка "Создать базы данных"
        self.create_btn = QPushButton("🗄️ Создать базы данных")
        self.create_btn.clicked.connect(self.create_databases)
        self.create_btn.setObjectName("createButton")
        self.create_btn.setMinimumWidth(150)

        # Кнопка "Очистить базы данных"
        self.clean_btn = QPushButton("🧹 Очистить базы данных")
        self.clean_btn.clicked.connect(self.clean_databases)
        self.clean_btn.setObjectName("cleanButton")
        self.clean_btn.setMinimumWidth(150)

        # Кнопка "Сохранить конфиг"
        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.clicked.connect(self.save_current_config)
        self.save_btn.setObjectName("saveButton")
        self.save_btn.setMinimumWidth(150)

        # Добавляем кнопки в контейнер
        button_container_layout.addWidget(self.create_btn)
        button_container_layout.addWidget(self.clean_btn)
        button_container_layout.addWidget(self.save_btn)

        # Центрируем контейнер с кнопками
        button_layout.addStretch()
        button_layout.addWidget(button_container)
        button_layout.addStretch()

        main_layout.addWidget(button_frame)

        # ===== 4. СЕКЦИЯ: Окно консоли =====
        console_group = QGroupBox("Консоль вывода")
        console_layout = QVBoxLayout()

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Courier New", 10))

        # Кнопка очистки консоли
        self.clear_btn = QPushButton("Очистить консоль")
        self.clear_btn.clicked.connect(self.clear_console)

        console_layout.addWidget(self.clear_btn)
        console_layout.addWidget(self.console_output)
        console_group.setLayout(console_layout)

        main_layout.addWidget(console_group, 1)

    def setup_status_bar(self):
        """Настройка статус бара с отображением версии и кнопкой темы"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Левая часть: обычные сообщения
        status_bar.showMessage("Готово")

        # Кнопка переключения темы
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.setFixedSize(30, 22)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setToolTip("Переключить тему")

        # Версия приложения
        version_widget = self.create_version_widget()

        # Добавляем элементы в статус бар (справа налево)
        status_bar.addPermanentWidget(self.theme_btn)
        status_bar.addPermanentWidget(version_widget)

        # Обновляем сообщения статуса через таймер
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_message)
        self.status_timer.start(5000)

    def create_version_widget(self):
        """Создает виджет с информацией о версии"""
        try:
            from version import get_version_string
            version_str = get_version_string()
        except ImportError:
            version_str = "v1.0.0"

        # Создаем контейнер для версии
        version_container = QWidget()
        layout = QHBoxLayout(version_container)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # Иконка
        icon_label = QLabel("⚡")
        icon_label.setToolTip("Статус приложения")

        # Текст версии
        version_text = f"<b>{version_str}</b>"
        version_label = QLabel(version_text)
        version_label.setObjectName("versionLabel")

        # Добавляем элементы
        layout.addWidget(icon_label)
        layout.addWidget(version_label)

        # Tooltip с полной информацией
        full_info = f"""<b>PSQL Mock Creator</b><br/>
                    Версия: {version_str}<br/>
                    Тема: {self.current_theme}<br/>
                    <br/>
                    Готов к работе."""
        version_container.setToolTip(full_info)

        return version_container

    def apply_theme(self, theme_name):
        """Применяет выбранную тему."""
        self.current_theme = theme_name

        # Сохраняем выбор темы
        self.settings.setValue("theme", theme_name)

        if theme_name == "dark":
            # Применяем темную тему
            self.setStyleSheet(DARK_THEME)
            self.theme_btn.setText("🌞")  # Солнце для переключения на светлую
            self.clear_btn.setStyleSheet(CONSOLE_BUTTON_STYLE_DARK)

            # Обновляем стиль виджета версии
            version_widget = self.statusBar().findChild(QWidget)
            if version_widget:
                version_widget.setStyleSheet(VERSION_WIDGET_STYLE_DARK)

            # Обновляем стили отключенных кнопок
            self.update_disabled_buttons_style(DISABLED_BUTTON_STYLE_DARK)

        else:
            # Применяем светлую тему
            self.setStyleSheet(LIGHT_THEME)
            self.theme_btn.setText("🌙")  # Луна для переключения на темную
            self.clear_btn.setStyleSheet(CONSOLE_BUTTON_STYLE_LIGHT)

            # Обновляем стиль виджета версии
            version_widget = self.statusBar().findChild(QWidget)
            if version_widget:
                version_widget.setStyleSheet(VERSION_WIDGET_STYLE_LIGHT)

            # Обновляем стили отключенных кнопок
            self.update_disabled_buttons_style(DISABLED_BUTTON_STYLE_LIGHT)

        # Логируем смену темы
        self.log_to_console(f"[THEME] Применена {theme_name} тема\n")

        # Обновляем статус бар
        self.statusBar().showMessage(f"Тема: {theme_name}", 2000)

    def update_disabled_buttons_style(self, style):
        """Обновляет стили для отключенных кнопок."""
        # Сохраняем текущее состояние кнопок
        create_enabled = self.create_btn.isEnabled()
        clean_enabled = self.clean_btn.isEnabled()
        save_enabled = self.save_btn.isEnabled()

        # Временно отключаем, чтобы применить стиль
        if not create_enabled:
            self.create_btn.setStyleSheet(style)
        else:
            self.create_btn.setStyleSheet("")

        if not clean_enabled:
            self.clean_btn.setStyleSheet(style)
        else:
            self.clean_btn.setStyleSheet("")

        if not save_enabled:
            self.save_btn.setStyleSheet(style)
        else:
            self.save_btn.setStyleSheet("")

    def toggle_theme(self):
        """Переключает тему между светлой и темной."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def update_status_message(self):
        """Обновляет сообщение в статус баре"""
        messages = [
            "Готов к работе",
            "Ожидание действий пользователя",
            "Базы данных: 4 доступно",
            f"Версия: {self.get_app_version()}",
            f"Тема: {self.current_theme}",
            f"Время: {datetime.now().strftime('%H:%M')}"
        ]

        current_message = self.statusBar().currentMessage()
        if current_message:
            try:
                idx = messages.index(current_message)
                next_idx = (idx + 1) % len(messages)
            except ValueError:
                next_idx = 0
        else:
            next_idx = 0

        self.statusBar().showMessage(messages[next_idx], 3000)

    def get_app_version(self):
        """Возвращает версию приложения"""
        try:
            from version import get_version_string
            return get_version_string()
        except ImportError:
            return "v1.0.0"

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
        return [db_id for db_id, checkbox in self.db_checkboxes.items() if checkbox.isChecked()]

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
        self.set_buttons_enabled(False)
        self.logger.start_logging()

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
                self.logger.stop_logging()
                self.set_buttons_enabled(True)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

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

        # Применяем/снимаем стиль для отключенных кнопок
        if not enabled:
            if self.current_theme == "dark":
                style = DISABLED_BUTTON_STYLE_DARK
            else:
                style = DISABLED_BUTTON_STYLE_LIGHT

            self.create_btn.setStyleSheet(style)
            self.clean_btn.setStyleSheet(style)
            self.save_btn.setStyleSheet(style)
        else:
            self.create_btn.setStyleSheet("")
            self.clean_btn.setStyleSheet("")
            self.save_btn.setStyleSheet("")

    def setup_console_updater(self):
        """Настраивает таймер для обновления консоли."""
        self.console_timer = QTimer()
        self.console_timer.timeout.connect(self.update_console_display)
        self.console_timer.start(100)

    def update_console_display(self):
        """Берет накопленные логи из OutputLogger и выводит в QTextEdit."""
        logs = self.logger.get_logs()
        if logs:
            self.console_output.moveCursor(QTextCursor.MoveOperation.End)
            self.console_output.insertPlainText(logs)
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