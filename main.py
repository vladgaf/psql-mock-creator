import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from core.config_manager import RESOURCES_DIR
from ui.main_window import MainWindow


def setup_app_icon(app):
    """Установка иконки приложения - используем ЕДИНЫЙ метод из config_manager"""

    possible_paths = [
        os.path.join(RESOURCES_DIR, 'icon.ico'),
        os.path.join(RESOURCES_DIR, 'icon.png')
    ]

    icon_set = False
    for path in possible_paths:
        try:
            if os.path.exists(path):
                app.setWindowIcon(QIcon(path))
                print(f"✅ Иконка приложения установлена из: {path}")
                icon_set = True
                break
        except Exception as e:
            print(f"⚠️ Ошибка загрузки иконки {path}: {e}")

    if not icon_set:
        print("⚠️ Иконка не найдена, используется иконка по умолчанию")

    return icon_set


def main():
    # Создаем приложение PyQt
    app = QApplication(sys.argv)
    setup_app_icon(app)
    app.setApplicationName("PSQL Mock Creator")

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
