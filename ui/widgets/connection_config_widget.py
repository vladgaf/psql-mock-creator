from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QLineEdit


class ConnectionConfigWidget(QGroupBox):
    def __init__(self):
        super().__init__("Настройки подключения к PostgreSQL")
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()

        # Поля ввода
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Добавляем поля с подписями
        layout.addWidget(QLabel("Хост:"), 0, 0)
        layout.addWidget(self.host_input, 0, 1)
        layout.addWidget(QLabel("Порт:"), 1, 0)
        layout.addWidget(self.port_input, 1, 1)
        layout.addWidget(QLabel("Пользователь:"), 2, 0)
        layout.addWidget(self.user_input, 2, 1)
        layout.addWidget(QLabel("Пароль:"), 3, 0)
        layout.addWidget(self.password_input, 3, 1)

        self.setLayout(layout)

    def get_config(self):
        """Возвращает текущие настройки как словарь."""
        return {
            'host': self.host_input.text().strip(),
            'port': int(self.port_input.text()) if self.port_input.text().isdigit() else 5432,
            'user': self.user_input.text().strip(),
            'password': self.password_input.text()
        }

    def load_config(self, config):
        """Загружает конфиг в поля ввода."""
        self.host_input.setText(config.get('host', 'localhost'))
        self.port_input.setText(str(config.get('port', 5432)))
        self.user_input.setText(config.get('user', 'postgres'))
        self.password_input.setText(config.get('password', ''))
