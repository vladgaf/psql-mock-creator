import threading
import traceback

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget, QMessageBox

from core.database_manager import DatabaseManager
from core.logger import QtOutputLogger
from ui.styles import DISABLED_BUTTON_STYLE_LIGHT, DISABLED_BUTTON_STYLE_DARK


# Класс для безопасной передачи данных между потоками (переносим из main_window)
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(str)


class ControlButtonsWidget(QFrame):
    """Виджет кнопок управления с полной логикой потоков."""

    # Сигналы для общения с main_window
    operation_started = pyqtSignal(str)  # сообщение для статус бара
    operation_finished = pyqtSignal(str)  # сообщение для статус бара
    config_saved = pyqtSignal()
    console_log = pyqtSignal(str)
    clear_console_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.active_workers = []
        self.current_theme = "light"
        self.logger = None
        self.console_output = None

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)

        # Контейнер для центрирования кнопок
        button_container = QWidget()
        button_container_layout = QHBoxLayout(button_container)
        button_container_layout.setSpacing(15)
        button_container_layout.setContentsMargins(0, 0, 0, 0)

        # Создание кнопок
        self.create_btn = self._create_button("🗄️ Создать базы данных", "createButton")
        self.clean_btn = self._create_button("🧹 Очистить базы данных", "cleanButton")
        self.save_btn = self._create_button("💾 Сохранить настройки", "saveButton")

        # Подключаем кнопки
        self.create_btn.clicked.connect(self.create_databases)
        self.clean_btn.clicked.connect(self.clean_databases)
        self.save_btn.clicked.connect(self.save_current_config)

        # Добавление в контейнер
        button_container_layout.addWidget(self.create_btn)
        button_container_layout.addWidget(self.clean_btn)
        button_container_layout.addWidget(self.save_btn)

        # Центрирование
        layout.addStretch()
        layout.addWidget(button_container)
        layout.addStretch()

    def _create_button(self, text, object_name):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setMinimumWidth(150)
        return button

    def set_logger(self, logger: QtOutputLogger):
        """Устанавливает логгер для этого виджета."""
        self.logger = logger

    def set_console_output(self, console_output):
        """Устанавливает ссылку на QTextEdit консоли."""
        self.console_output = console_output

    def set_current_theme(self, theme):
        """Устанавливает текущую тему."""
        self.current_theme = theme

    # ========== ОРИГИНАЛЬНЫЕ МЕТОДЫ ИЗ MAIN_WINDOW ==========

    def create_databases(self):
        """Обработчик кнопки 'Создать базы данных' ."""
        # Получаем данные из main_window
        if not self.main_window:
            return

        selected = self.main_window.get_selected_databases()
        if not selected:
            QMessageBox.warning(self.main_window, "Внимание", "Выберите хотя бы одну базу данных!")
            return

        config = self.main_window.get_current_config()
        self.run_database_operation("create", selected, config)

    def clean_databases(self):
        """Обработчик кнопки 'Очистить базы данных' ."""
        if not self.main_window:
            return

        selected = self.main_window.get_selected_databases()
        if not selected:
            QMessageBox.warning(self.main_window, "Внимание", "Выберите хотя бы одну базу данных!")
            return

        reply = QMessageBox.question(
            self.main_window, 'Подтверждение',
            f'Вы уверены, что хотите очистить {len(selected)} баз данных?\nЭто действие удалит все данные.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            config = self.main_window.get_current_config()
            self.run_database_operation("clean", selected, config)

    def save_current_config(self):
        """Сохраняет текущие настройки в файл."""
        if not self.main_window:
            return

        self.main_window.save_current_config()
        self.config_saved.emit()

    def run_database_operation(self, operation, databases, config):
        """Запускает операцию с БД в отдельном потоке ."""
        self.set_buttons_enabled(False)

        if self.logger:
            self.logger.start_logging()

        # Создаем объект сигналов для этого потока
        worker_signals = WorkerSignals()
        worker_signals.finished.connect(lambda: self.on_worker_finished(worker_signals))
        worker_signals.error.connect(self.on_worker_error)
        worker_signals.log.connect(self.on_worker_log)

        def worker():
            try:
                db_manager = DatabaseManager(config)
                if operation == "create":
                    db_manager.create_databases(databases)
                else:
                    db_manager.clean_databases(databases)
                worker_signals.finished.emit()
            except Exception as e:
                error_msg = f"[ERROR] Ошибка: {e}\n{traceback.format_exc()}"
                worker_signals.error.emit(error_msg)

        thread = threading.Thread(target=worker, daemon=True)
        self.active_workers.append((thread, worker_signals))

        thread.start()

        op_name = "создание" if operation == "create" else "очистка"
        self.log_to_console(f"\n{'=' * 60}\n")
        self.log_to_console(f"Запуск {op_name} баз данных: {', '.join(databases)}\n")
        self.log_to_console(f"{'=' * 60}\n\n")

        self.operation_started.emit(f"Выполняется {op_name}...")

    @pyqtSlot()
    def on_worker_finished(self, worker_signals):
        """Слот для завершения работы потока ."""
        # Удаляем завершенный поток из списка активных
        for i, (thread, signals) in enumerate(self.active_workers):
            if signals == worker_signals:
                self.active_workers.pop(i)
                break

        if self.logger:
            self.logger.stop_logging()

        self.set_buttons_enabled(True)
        self.operation_finished.emit("Операция завершена")

    @pyqtSlot(str)
    def on_worker_error(self, error_msg):
        """Слот для обработки ошибок из потока ."""
        print(error_msg)  # Вывод в системную консоль
        self.log_to_console(error_msg)  # Вывод в UI консоль
        self.set_buttons_enabled(True)

        if self.logger:
            self.logger.stop_logging()

    @pyqtSlot(str)
    def on_worker_log(self, log_msg):
        """Слот для получения логов из потока ."""
        self.log_to_console(log_msg)

    def log_to_console(self, message):
        """Прямой вывод сообщения в консоль."""
        if self.console_output:
            self.console_output.moveCursor(QTextCursor.MoveOperation.End)
            self.console_output.insertPlainText(message)
            self.console_output.ensureCursorVisible()
        else:
            # Если нет прямой ссылки, используем сигнал
            self.console_log.emit(message)

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

    def cleanup(self):
        """Очистка ресурсов при закрытии."""
        print(f"Ожидание завершения {len(self.active_workers)} активных потоков...")
        for thread, _ in self.active_workers:
            if thread.is_alive():
                thread.join(timeout=2.0)
