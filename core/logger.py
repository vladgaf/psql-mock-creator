import sys
from io import StringIO


class OutputLogger:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.log_buffer = StringIO()
        self.console_output = ""

    def start_logging(self):
        """Начинает перехват вывода в stdout."""
        sys.stdout = self

    def stop_logging(self):
        """Останавливает перехват и восстанавливает stdout."""
        sys.stdout = self.original_stdout

    def write(self, message):
        """Перехватывает запись в stdout."""
        self.original_stdout.write(message)  # Вывод в реальную консоль (опционально)
        self.log_buffer.write(message)
        self.console_output += message

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
