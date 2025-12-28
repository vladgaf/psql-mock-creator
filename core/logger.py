import sys
from io import StringIO
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class QtOutputLogger(QObject):
    """
    Безопасный логгер для работы с Qt из разных потоков.
    Сохраняет всю функциональность OutputLogger + потокобезопасность.
    """
    # Сигнал для передачи логов в главный поток Qt
    log_updated_signal = pyqtSignal(str)

    def __init__(self, text_widget=None):
        super().__init__()
        self.original_stdout = sys.stdout
        self.log_buffer = StringIO()
        self.console_output = ""
        self.text_widget = text_widget

        # Связываем сигнал со слотом обновления виджета
        if text_widget:
            self.log_updated_signal.connect(self._update_text_widget)

    @pyqtSlot(str)
    def _update_text_widget(self, message):
        """Слот для обновления QTextEdit (выполняется в главном потоке)"""
        if self.text_widget:
            self.text_widget.append(message)
            # Автопрокрутка
            scrollbar = self.text_widget.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())

    def start_logging(self):
        """Начинает перехват вывода в stdout."""
        sys.stdout = self

    def stop_logging(self):
        """Останавливает перехват и восстанавливает stdout."""
        sys.stdout = self.original_stdout

    def write(self, message):
        """Перехватывает запись в stdout. Потокобезопасная версия."""
        # Вывод в реальную консоль
        self.original_stdout.write(message)

        # Сохранить в буфер
        self.log_buffer.write(message)
        self.console_output += message

        # 3. Обновить QTextEdit через сигнал
        if self.text_widget and message.strip():
            self.log_updated_signal.emit(message)

    def flush(self):
        """Метод, требуемый для объекта, заменяющего stdout."""
        self.original_stdout.flush()

    def get_logs(self):
        """Возвращает текущий вывод и очищает буфер."""
        logs = self.console_output
        self.console_output = ""
        self.log_buffer.truncate(0)
        self.log_buffer.seek(0)
        return logs

    def set_text_widget(self, text_widget):
        """Динамическая установка/изменение QTextEdit."""
        self.text_widget = text_widget
        if text_widget:
            # Переподключаем сигнал если виджет изменился
            try:
                self.log_updated_signal.disconnect()
            except:
                pass
            self.log_updated_signal.connect(self._update_text_widget)