import os
import sys
from datetime import datetime

from PyQt6.QtCore import QTimer, QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStatusBar, QPushButton
)

from core.config_manager import get_postgres_config, save_postgres_config, RESOURCES_DIR
from core.logger import QtOutputLogger
from ui.styles import (
    LIGHT_THEME, DARK_THEME,
    VERSION_WIDGET_STYLE_LIGHT, VERSION_WIDGET_STYLE_DARK,
    CONSOLE_BUTTON_STYLE_LIGHT, CONSOLE_BUTTON_STYLE_DARK
)
from ui.widgets.connection_config_widget import ConnectionConfigWidget
from ui.widgets.console_output_widget import ConsoleOutputWidget
from ui.widgets.control_buttons_widget import ControlButtonsWidget
from ui.widgets.database_selection_widget import DatabaseSelectionWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(self.get_app_icon())

        # Загрузка настроек темы
        self.settings = QSettings("PSQLMockCreator", "AppSettings")
        self.current_theme = self.settings.value("theme", "light", type=str)

        self.setup_ui()
        self.setup_status_bar()
        self.load_saved_config()
        self.setup_logger()
        self.connect_signals()

        # Применяем сохраненную тему
        self.apply_theme(self.current_theme)

    @staticmethod
    def get_app_icon():
        possible_paths = [
            os.path.join(RESOURCES_DIR, 'icon.ico'),
            os.path.join(RESOURCES_DIR, 'icon.png')
        ]

        for path in possible_paths:
            try:
                if os.path.exists(path):
                    return QIcon(path)
            except:
                continue

        return QIcon.fromTheme("application-x-executable")

    def setup_ui(self):
        """Создает все элементы интерфейса."""
        self.setWindowTitle("PSQL Mock Creator")
        self.setGeometry(100, 100, 900, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Виджет настроек подключения
        self.connection_widget = ConnectionConfigWidget()
        main_layout.addWidget(self.connection_widget)

        # 2. Виджет выбора баз данных
        self.db_selection_widget = DatabaseSelectionWidget()
        main_layout.addWidget(self.db_selection_widget)

        # 3. Виджет кнопок управления (ВСЯ логика потоков теперь здесь!)
        self.control_buttons = ControlButtonsWidget(self)
        self.control_buttons.set_current_theme(self.current_theme)
        main_layout.addWidget(self.control_buttons)

        # 4. Виджет консоли
        self.console_widget = ConsoleOutputWidget()
        main_layout.addWidget(self.console_widget, 1)

    def setup_status_bar(self):
        """Настройка статус бара с отображением версии и кнопкой темы"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Левая часть: обычные сообщения
        status_bar.showMessage("Готово")

        # Кнопка переключения темы
        self.theme_btn = self.create_theme_button()

        # Версия приложения
        version_widget = self.create_version_widget()

        # Добавляем элементы в статус бар
        status_bar.addPermanentWidget(self.theme_btn)
        status_bar.addPermanentWidget(version_widget)

        # Обновляем сообщения статуса через таймер
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_message)
        self.status_timer.start(5000)

    def create_theme_button(self):
        """Создает кнопку переключения темы."""
        theme_btn = QPushButton()
        theme_btn.setObjectName("themeButton")
        theme_btn.setFixedSize(30, 22)
        theme_btn.clicked.connect(self.toggle_theme)
        theme_btn.setToolTip("Переключить тему")

        # Устанавливаем начальную иконку
        theme_btn.setText("🌙" if self.current_theme == "light" else "🌞")

        return theme_btn

    def create_version_widget(self):
        """Создает виджет с информацией о версии"""
        try:
            from version import get_version_string
            version_str = get_version_string()
        except ImportError:
            version_str = "v1.0.0"

        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

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

    def setup_logger(self):
        """Настраивает логгер и связывает его с виджетом кнопок."""
        # Передаем QTextEdit из виджета консоли в логгер
        self.logger = QtOutputLogger(self.console_widget.get_text_widget())
        self.logger.start_logging()

        # Передаем логгер в виджет кнопок
        self.control_buttons.set_logger(self.logger)
        self.control_buttons.set_console_output(self.console_widget.get_text_widget())

        # Настраиваем таймер для обновления консоли
        self.console_timer = QTimer()
        self.console_timer.timeout.connect(self.update_console_display)
        self.console_timer.start(100)

    def connect_signals(self):
        """Подключает сигналы между компонентами."""
        # Кнопка очистки консоли
        self.console_widget.clear_btn.clicked.connect(self.console_widget.clear)

        # Сигналы от виджета кнопок
        self.control_buttons.operation_started.connect(
            lambda msg: self.statusBar().showMessage(msg)
        )
        self.control_buttons.operation_finished.connect(
            lambda msg: self.statusBar().showMessage(msg, 3000)
        )
        self.control_buttons.config_saved.connect(
            lambda: self.statusBar().showMessage("Настройки сохранены", 3000)
        )
        self.control_buttons.console_log.connect(
            self.console_widget.log_message
        )

    def update_console_display(self):
        """Обновляет отображение консоли."""
        if hasattr(self, 'logger'):
            logs = self.logger.get_logs()
            if logs:
                self.console_widget.log_message(logs)

    def apply_theme(self, theme_name):
        """Применяет выбранную тему."""
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)

        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME)
            self.theme_btn.setText("🌞")
            self.console_widget.set_clear_button_style(CONSOLE_BUTTON_STYLE_DARK)

            # Обновляем стиль виджета версии
            version_widget = self.statusBar().findChild(QWidget)
            if version_widget:
                version_widget.setStyleSheet(VERSION_WIDGET_STYLE_DARK)

        else:
            self.setStyleSheet(LIGHT_THEME)
            self.theme_btn.setText("🌙")
            self.console_widget.set_clear_button_style(CONSOLE_BUTTON_STYLE_LIGHT)

            # Обновляем стиль виджета версии
            version_widget = self.statusBar().findChild(QWidget)
            if version_widget:
                version_widget.setStyleSheet(VERSION_WIDGET_STYLE_LIGHT)

        # Обновляем тему в виджете кнопок
        self.control_buttons.set_current_theme(theme_name)

        # Логируем смену темы
        self.console_widget.log_message(f"[THEME] Применена {theme_name} тема\n")
        self.statusBar().showMessage(f"Тема: {theme_name}", 2000)

    def toggle_theme(self):
        """Переключает тему между светлой и темной."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def update_status_message(self):
        """Обновляет сообщение в статус баре."""
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
        """Возвращает версию приложения."""
        try:
            from version import get_version_string
            return get_version_string()
        except ImportError:
            return "v1.0.0"

    def load_saved_config(self):
        """Загружает сохраненный конфиг в поля ввода."""
        config = get_postgres_config()
        self.connection_widget.load_config(config)

    def get_current_config(self):
        """Возвращает текущие настройки из полей ввода как словарь."""
        return self.connection_widget.get_config()

    def get_selected_databases(self):
        """Возвращает список ID выбранных баз данных."""
        return self.db_selection_widget.get_selected_databases()

    def save_current_config(self):
        """Сохраняет текущие настройки в файл."""
        config = self.get_current_config()
        save_postgres_config(config)
        self.console_widget.log_message("[INFO] Настройки сохранены в config/postgres.json\n")

    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        print("Начало корректного закрытия приложения...")

        # 1. Останавливаем все таймеры
        if hasattr(self, 'console_timer'):
            self.console_timer.stop()
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()

        # 2. Очищаем ресурсы виджета кнопок (ждем завершения потоков)
        if hasattr(self, 'control_buttons'):
            self.control_buttons.cleanup()

        # 3. Останавливаем логгирование
        if hasattr(self, 'logger'):
            self.logger.stop_logging()

        # 4. Сохраняем настройки
        self.settings.setValue("theme", self.current_theme)

        # 5. Вызываем явный flush для stdout
        sys.stdout.flush()

        print("Приложение корректно завершено.")
        super().closeEvent(event)
