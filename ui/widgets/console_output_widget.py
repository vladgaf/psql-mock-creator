from datetime import datetime

from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QPushButton


class ConsoleOutputWidget(QGroupBox):
    def __init__(self):
        super().__init__("Консоль вывода")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Courier New", 10))

        self.clear_btn = QPushButton("Очистить консоль")

        layout.addWidget(self.clear_btn)
        layout.addWidget(self.console_output)
        self.setLayout(layout)

    def get_text_widget(self):
        """Возвращает QTextEdit для логгера."""
        return self.console_output

    def log_message(self, message):
        """Добавляет сообщение в консоль."""
        self.console_output.moveCursor(QTextCursor.MoveOperation.End)
        self.console_output.insertPlainText(message)
        self.console_output.ensureCursorVisible()

    def clear(self):
        """Очищает консоль."""
        self.console_output.clear()
        self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] Консоль очищена\n")

    def set_clear_button_style(self, style):
        """Устанавливает стиль кнопки очистки."""
        self.clear_btn.setStyleSheet(style)
