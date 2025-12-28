"""
Стили для PyQt6 приложения PSQL Mock Creator
Светлая и темная темы
"""

# ==================== СВЕТЛАЯ ТЕМА (Light Theme) ====================
LIGHT_THEME = """
/* Основное окно */
QMainWindow {
    background-color: #f0f0f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #333333;
}

/* Группы с рамкой */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    border: 2px solid #cccccc;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: white;
    color: #333333;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: #333333;
    border-radius: 5px;
    border: 1px solid #444444;
    background-color: white;
}

/* Поля ввода */
QLineEdit, QSpinBox {
    padding: 8px;
    border: 1px solid #aaaaaa;
    border-radius: 4px;
    background-color: white;
    color: #333333;
    font-size: 13px;
    selection-background-color: #4CAF50;
    selection-color: white;
}

QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #4CAF50;
}

/* Кнопки */
QPushButton {
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    font-size: 13px;
    border: none;
    min-width: 100px;
}

QPushButton:hover {
    opacity: 0.9;
}

QPushButton#createButton {
    background-color: #4CAF50;
    color: white;
}

QPushButton#cleanButton {
    background-color: #f44336;
    color: white;
}

QPushButton#saveButton {
    background-color: #2196F3;
    color: white;
}

/* Консоль вывода */
QTextEdit {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 5px;
    selection-background-color: #264F78;
}

/* Чекбоксы */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    padding: 4px;
    color: #333333;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #bdc3c7;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:hover {
    border: 2px solid #95a5a6;
}

QCheckBox::indicator:checked {
    border: 2px solid #4CAF50;
    background-color: #4CAF50;
}

QCheckBox:disabled {
    color: #95a5a6;
}

QCheckBox::indicator:disabled {
    border: 2px solid #ecf0f1;
    background-color: #f8f9fa;
}

QCheckBox::indicator:checked:disabled {
    border: 2px solid #bdc3c7;
    background-color: #bdc3c7;
}

/* Статус бар */
QStatusBar {
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    color: #6c757d;
    font-size: 11px;
}

QStatusBar::item {
    border: none;
}

/* Версия в статус баре */
QLabel#versionLabel {
    color: #495057;
    font-weight: bold;
    padding: 2px 6px;
    background-color: rgba(108, 117, 125, 0.1);
    border-radius: 3px;
    border: 1px solid rgba(108, 117, 125, 0.2);
}

/* Кнопка темы для светлой темы */
QPushButton#themeButton {
    background-color: rgba(108, 117, 125, 0.1);
    border: 1px solid rgba(108, 117, 125, 0.2);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 12px;
    min-width: 30px;
    max-width: 30px;
    min-height: 22px;
    max-height: 22px;
}

QPushButton#themeButton:hover {
    background-color: rgba(108, 117, 125, 0.2);
}

/* Всплывающие окна */
QMessageBox {
    background-color: white;
}

QMessageBox QLabel {
    color: #333333;
}
"""

# ==================== ТЕМНАЯ ТЕМА (Dark Theme) ====================
DARK_THEME = """
/* Основное окно */
QMainWindow {
    background-color: #1e1e1e;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #e0e0e0;
}

/* Группы с рамкой */
/* Группы с рамкой */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    border: 2px solid #444444;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: #e0e0e0;
    background-color: #2d2d2d;
    border-radius: 5px;
    border: 1px solid #444444;
    padding: 2px 5px;
}

/* Поля ввода */
QLineEdit, QSpinBox {
    padding: 8px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #333333;
    color: #e0e0e0;
    font-size: 13px;
    selection-background-color: #4CAF50;
    selection-color: white;
}

QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #4CAF50;
}

/* Кнопки */
QPushButton {
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    font-size: 13px;
    border: none;
    min-width: 100px;
}

QPushButton:hover {
    opacity: 0.9;
}

QPushButton#createButton {
    background-color: #4CAF50;
    color: white;
}

QPushButton#cleanButton {
    background-color: #f44336;
    color: white;
}

QPushButton#saveButton {
    background-color: #2196F3;
    color: white;
}

/* Консоль вывода - в темной теме светлее */
QTextEdit {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    background-color: #252525;
    color: #cccccc;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 5px;
    selection-background-color: #264F78;
}

/* Чекбоксы */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    padding: 4px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #555555;
    border-radius: 3px;
    background-color: #333333;
}

QCheckBox::indicator:hover {
    border: 2px solid #777777;
}

QCheckBox::indicator:checked {
    border: 2px solid #4CAF50;
    background-color: #4CAF50;
}

QCheckBox:disabled {
    color: #777777;
}

QCheckBox::indicator:disabled {
    border: 2px solid #444444;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked:disabled {
    border: 2px solid #555555;
    background-color: #555555;
}

/* Статус бар */
QStatusBar {
    background-color: #252525;
    border-top: 1px solid #444444;
    color: #aaaaaa;
    font-size: 11px;
}

QStatusBar::item {
    border: none;
}

/* Версия в статус баре */
QLabel#versionLabel {
    color: #cccccc;
    font-weight: bold;
    padding: 2px 6px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Кнопка темы для темной темы */
QPushButton#themeButton {
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 12px;
    min-width: 30px;
    max-width: 30px;
    min-height: 22px;
    max-height: 22px;
    color: #e0e0e0;
}

QPushButton#themeButton:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

/* Всплывающие окна */
QMessageBox {
    background-color: #2d2d2d;
}

QLabel{
    color: white;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

QMessageBox QPushButton {
    background-color: #444444;
    color: #e0e0e0;
}

QMessageBox QPushButton:hover {
    background-color: #555555;
}
"""

# Для обратной совместимости
APP_STYLESHEET = LIGHT_THEME

# Стили для виджета версии (адаптивные)
VERSION_WIDGET_STYLE_LIGHT = """
QWidget {
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
    padding: 2px;
}
"""

VERSION_WIDGET_STYLE_DARK = """
QWidget {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
    padding: 2px;
}
"""

# Стили для кнопки консоли
CONSOLE_BUTTON_STYLE_LIGHT = """
QPushButton {
    background-color: #6c757d;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: normal;
}

QPushButton:hover {
    background-color: #5a6268;
}
"""

CONSOLE_BUTTON_STYLE_DARK = """
QPushButton {
    background-color: #555555;
    color: #e0e0e0;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: normal;
}

QPushButton:hover {
    background-color: #666666;
}
"""

# Для обратной совместимости
CONSOLE_BUTTON_STYLE = CONSOLE_BUTTON_STYLE_LIGHT
VERSION_WIDGET_STYLE = VERSION_WIDGET_STYLE_LIGHT

# Стили для отключенных кнопок
DISABLED_BUTTON_STYLE_LIGHT = """
QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
    opacity: 0.7;
}
"""

DISABLED_BUTTON_STYLE_DARK = """
QPushButton:disabled {
    background-color: #555555;
    color: #888888;
    opacity: 0.7;
}
"""

# Для обратной совместимости
DISABLED_BUTTON_STYLE = DISABLED_BUTTON_STYLE_LIGHT