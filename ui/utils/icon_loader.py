import os

from PyQt6.QtGui import QIcon

from core.config_manager import RESOURCES_DIR


def get_app_icon():
    """
    Загружает иконку приложения из ресурсов.
    Возвращает QIcon или стандартную иконку Qt.
    """
    # Сначала пробуем найти в файловой системе
    possible_paths = [
        os.path.join(RESOURCES_DIR, 'icon.ico'),
        os.path.join(RESOURCES_DIR, 'icon.png'),
        os.path.join(RESOURCES_DIR, 'icon.svg'),
        os.path.join(RESOURCES_DIR, 'icon.icns'),  # для macOS
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                return QIcon(path)
            except:
                continue

    return QIcon.fromTheme("application-x-executable")
