from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QStatusBar, QPushButton, QWidget, QHBoxLayout, QLabel


class StatusBarComponent:
    def __init__(self, main_window, theme_manager):
        self.main_window = main_window
        self.theme_manager = theme_manager
        self.status_bar = QStatusBar()
        self.status_messages = [
            "Готов к работе",
            "Ожидание действий пользователя",
            "Базы данных: 4 доступно",
            f"Версия: {self._get_app_version()}",
            f"Тема: {self.theme_manager.current_theme}",
            f"Время: {datetime.now().strftime('%H:%M')}"
        ]

    def setup(self):
        """Настраивает статус бар."""
        self.main_window.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")

        self.theme_btn = self._create_theme_button()
        self.version_widget = self._create_version_widget()

        self.status_bar.addPermanentWidget(self.theme_btn)
        self.status_bar.addPermanentWidget(self.version_widget)

        self._setup_status_timer()

    def _create_theme_button(self) -> QPushButton:
        """Создает кнопку переключения темы."""
        btn = QPushButton()
        btn.setObjectName("themeButton")
        btn.setFixedSize(30, 22)
        btn.setToolTip("Переключить тему")

        # Устанавливаем начальный текст в зависимости от темы
        btn.setText("🌙" if self.theme_manager.current_theme == "light" else "🌞")

        return btn

    def _create_version_widget(self) -> QWidget:
        """Создает виджет с информацией о версии."""
        try:
            from version import get_version_string
            version_str = get_version_string()
        except ImportError:
            version_str = "v1.0.0"

        # Создаем контейнер
        version_container = QWidget()
        layout = QHBoxLayout(version_container)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # Иконка
        icon_label = QLabel("⚡")
        icon_label.setToolTip("Статус приложения")

        # Текст версии
        version_text = f"<b>{version_str}</b>"
        version_label = QLabel(version_text)
        version_label.setObjectName("versionLabel")

        # Добавляем элементы
        layout.addWidget(icon_label)
        layout.addWidget(version_label)

        # Tooltip с полной информацией
        full_info = f"""<b>PSQL Mock Creator</b><br/>
                    Версия: {version_str}<br/>
                    Тема: {self.theme_manager.current_theme}<br/>
                    <br/>
                    Готов к работе."""
        version_container.setToolTip(full_info)

        return version_container

    def _setup_status_timer(self):
        """Настраивает таймер для обновления статусных сообщений."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_message)
        self.status_timer.start(5000)

    def update_status_message(self):
        """Обновляет сообщение в статус баре."""
        current_message = self.status_bar.currentMessage()

        if current_message:
            try:
                idx = self.status_messages.index(current_message)
                next_idx = (idx + 1) % len(self.status_messages)
            except ValueError:
                next_idx = 0
        else:
            next_idx = 0

        self.status_bar.showMessage(self.status_messages[next_idx], 3000)

    def _get_app_version(self) -> str:
        """Возвращает версию приложения."""
        try:
            from version import get_version_string
            return get_version_string()
        except ImportError:
            return "v1.0.0"

    def update_theme_button(self):
        """Обновляет кнопку темы в зависимости от текущей темы."""
        if self.theme_manager.current_theme == "light":
            self.theme_btn.setText("🌙")
        else:
            self.theme_btn.setText("🌞")

    def show_temporary_message(self, message: str, timeout: int = 3000):
        """Показывает временное сообщение в статус баре."""
        self.status_bar.showMessage(message, timeout)

    def stop_timer(self):
        """Останавливает таймер обновления статуса."""
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
