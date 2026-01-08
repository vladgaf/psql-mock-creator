import threading
import traceback
from typing import List, Dict, Callable

from PyQt6.QtCore import QObject, pyqtSignal, QMetaObject, Qt, Q_ARG


class WorkerSignals(QObject):
    """Сигналы для безопасной передачи данных между потоками."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    progress = pyqtSignal(int)


class WorkerManager:
    def __init__(self):
        self.active_workers: List[tuple] = []

    def run_database_operation(self, operation: str, databases: List[str],
                               config: Dict, callbacks: Dict[str, Callable]) -> tuple:
        """
        Запускает операцию с БД в отдельном потоке.
        """
        worker_signals = WorkerSignals()

        def worker():
            try:
                from core.database_manager import DatabaseManager
                db_manager = DatabaseManager(config)

                if operation == "create":
                    db_manager.create_databases(databases)
                elif operation == "clean":
                    db_manager.clean_databases(databases)
                else:
                    raise ValueError(f"Неизвестная операция: {operation}")

                # Эмитируем сигнал в главном потоке
                QMetaObject.invokeMethod(
                    worker_signals,
                    "finished",
                    Qt.ConnectionType.QueuedConnection
                )

            except Exception as e:
                error_msg = f"[ERROR] Ошибка: {e}\n{traceback.format_exc()}"
                # Эмитируем ошибку в главном потоке
                QMetaObject.invokeMethod(
                    worker_signals,
                    "error",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, error_msg)
                )

        thread = threading.Thread(target=worker, daemon=True)
        self.active_workers.append((thread, worker_signals))

        # Подключаем сигналы к callback-функциям
        worker_signals.finished.connect(callbacks.get('finished', lambda: None))
        worker_signals.error.connect(callbacks.get('error', lambda x: None))
        worker_signals.log.connect(callbacks.get('log', lambda x: None))

        thread.start()
        return thread, worker_signals

    def wait_for_completion(self, timeout: float = 2.0) -> None:
        """Ожидает завершения всех активных потоков."""
        for thread, _ in self.active_workers:
            if thread.is_alive():
                thread.join(timeout=timeout)

    def cleanup(self) -> None:
        """Очищает список завершенных работников."""
        self.active_workers = [(t, s) for t, s in self.active_workers if t.is_alive()]

    def has_active_workers(self) -> bool:
        """Проверяет, есть ли активные потоки."""
        return any(t.is_alive() for t, _ in self.active_workers)

    def get_active_count(self) -> int:
        """Возвращает количество активных потоков."""
        return sum(1 for t, _ in self.active_workers if t.is_alive())
