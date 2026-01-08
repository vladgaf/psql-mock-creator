from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget

from ui.styles import (
    LIGHT_THEME, DARK_THEME,
    VERSION_WIDGET_STYLE_LIGHT, VERSION_WIDGET_STYLE_DARK,
    CONSOLE_BUTTON_STYLE_LIGHT, CONSOLE_BUTTON_STYLE_DARK,
    DISABLED_BUTTON_STYLE_LIGHT, DISABLED_BUTTON_STYLE_DARK
)


class ThemeManager:
    def __init__(self):
        self.settings = QSettings("PSQLMockCreator", "AppSettings")
        self.current_theme = self.settings.value("theme", "light", type=str)

    def apply_theme(self, theme_name, main_window):
        """Применяет тему ко всему окну и его компонентам."""
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)

        if theme_name == "dark":
            self._apply_dark_theme(main_window)
        else:
            self._apply_light_theme(main_window)

        # Логируем смену темы
        if hasattr(main_window, 'console_widget'):
            main_window.console_widget.log_message(f"[THEME] Применена {theme_name} тема\n")

        # Обновляем статус бар
        main_window.statusBar().showMessage(f"Тема: {theme_name}", 2000)

    def _apply_dark_theme(self, main_window):
        """Применяет темную тему."""
        main_window.setStyleSheet(DARK_THEME)

        # Обновляем кнопку темы
        if hasattr(main_window, 'status_bar_component'):
            main_window.status_bar_component.theme_btn.setText("🌞")

        # Обновляем стиль консольной кнопки
        if hasattr(main_window, 'console_widget'):
            main_window.console_widget.clear_btn.setStyleSheet(CONSOLE_BUTTON_STYLE_DARK)

        # Обновляем стиль виджета версии
        self._update_version_widget_style(main_window, VERSION_WIDGET_STYLE_DARK)

        # Обновляем стили отключенных кнопок
        self._update_disabled_buttons_style(main_window, DISABLED_BUTTON_STYLE_DARK)

    def _apply_light_theme(self, main_window):
        """Применяет светлую тему."""
        main_window.setStyleSheet(LIGHT_THEME)

        # Обновляем кнопку темы
        if hasattr(main_window, 'status_bar_component'):
            main_window.status_bar_component.theme_btn.setText("🌙")

        # Обновляем стиль консольной кнопки
        if hasattr(main_window, 'console_widget'):
            main_window.console_widget.clear_btn.setStyleSheet(CONSOLE_BUTTON_STYLE_LIGHT)

        # Обновляем стиль виджета версии
        self._update_version_widget_style(main_window, VERSION_WIDGET_STYLE_LIGHT)

        # Обновляем стили отключенных кнопок
        self._update_disabled_buttons_style(main_window, DISABLED_BUTTON_STYLE_LIGHT)

    def _update_version_widget_style(self, main_window, style):
        """Обновляет стиль виджета версии."""
        if hasattr(main_window, 'status_bar_component'):
            version_widget = main_window.statusBar().findChild(QWidget)
            if version_widget:
                version_widget.setStyleSheet(style)

    def _update_disabled_buttons_style(self, main_window, style):
        """Обновляет стили для отключенных кнопок."""
        if hasattr(main_window, 'control_buttons'):
            buttons = [
                main_window.control_buttons.create_btn,
                main_window.control_buttons.clean_btn,
                main_window.control_buttons.save_btn
            ]

            for button in buttons:
                if not button.isEnabled():
                    button.setStyleSheet(style)
                else:
                    button.setStyleSheet("")

    def toggle_theme(self, main_window):
        """Переключает тему между светлой и темной."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme, main_window)
