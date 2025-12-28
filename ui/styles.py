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
    border: 2px solid red;
}

QCheckBox::indicator:checked {
    background-color: #4CAF50;
    border: 2px solid #388E3C;
}
"""