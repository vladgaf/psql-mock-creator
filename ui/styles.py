"""
Стили для PyQt6 приложения PSQL Mock Creator
"""

APP_STYLESHEET = """
/* Основное окно */
QMainWindow {
    background-color: #f0f0f0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Группы с рамкой (Config, Database selection) */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    border: 2px solid #cccccc;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: #333333;
}

/* Поля ввода */
QLineEdit, QSpinBox {
    padding: 8px;
    border: 1px solid #aaaaaa;
    border-radius: 4px;
    background-color: white;
    font-size: 13px;
    selection-background-color: #4CAF50;
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
    background-color: #4CAF50;  /* Зеленый */
    color: white;
}

QPushButton#cleanButton {
    background-color: #f44336;  /* Красный */
    color: white;
}

QPushButton#saveButton {
    background-color: #2196F3;  /* Синий */
    color: white;
}

/* Консоль вывода */
QTextEdit {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    background-color: #1e1e1e;  /* Темный фон */
    color: #d4d4d4;             /* Светлый текст */
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 5px;
}

/* Чекбоксы */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    padding: 4px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid grey;
}

QCheckBox::indicator:checked {
    background-color: #4CAF50;
    border: 1px solid #388E3C;
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

QLabel#buildLabel {
    color: #868e96;
    font-size: 9px;
}
"""

# Дополнительные стили для виджета версии
VERSION_WIDGET_STYLE = """
QWidget {
    border-radius: 3px;
    padding: 2px;
}
"""

# Стили для кнопки очистки консоли
CONSOLE_BUTTON_STYLE = """
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

# Стили для полей ввода при ошибке
ERROR_FIELD_STYLE = """
QLineEdit {
    border: 2px solid #f44336;
    background-color: #fff5f5;
}
"""

# Стили для полей ввода при успехе
SUCCESS_FIELD_STYLE = """
QLineEdit {
    border: 2px solid #4CAF50;
}
"""

# Стили для кнопок в отключенном состоянии
DISABLED_BUTTON_STYLE = """
QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
    opacity: 0.7;
}
"""

# Стили для выделенного текста в консоли
CONSOLE_HIGHLIGHT_STYLES = {
    'success': 'color: #4CAF50; font-weight: bold;',
    'error': 'color: #f44336; font-weight: bold;',
    'warning': 'color: #ff9800; font-weight: bold;',
    'info': 'color: #2196F3; font-weight: normal;',
    'timestamp': 'color: #9e9e9e; font-style: italic;',
}

# Цветовая палитра приложения
COLOR_PALETTE = {
    'primary': '#2196F3',
    'secondary': '#4CAF50',
    'danger': '#f44336',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'success': '#28a745',
    'background': '#f0f0f0',
    'console_bg': '#1e1e1e',
    'console_text': '#d4d4d4',
}