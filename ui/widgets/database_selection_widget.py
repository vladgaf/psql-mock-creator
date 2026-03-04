from PyQt6.QtWidgets import QGroupBox, QGridLayout, QCheckBox


class DatabaseSelectionWidget(QGroupBox):
    DATABASES = [
        ("games_easy", "🎮 Простая база видеоигр (2 таблицы)"),
        ("school_world", "🏫 Школьная база данных (5 таблиц)"),
        ("games_shop", "🛒 Магазин видеоигр (4 таблицы)"),
        ("air_travel", "✈️ Авиакомпании и перелеты (5 таблиц)")
    ]

    def __init__(self):
        super().__init__("Выберите базы данных для создания")
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        self.db_checkboxes = {}

        for i, (db_id, db_label) in enumerate(self.DATABASES):
            checkbox = QCheckBox(db_label)
            checkbox.setChecked(True)
            self.db_checkboxes[db_id] = checkbox
            layout.addWidget(checkbox, i // 2, i % 2)

        self.setLayout(layout)

    def get_selected_databases(self):
        """Возвращает список ID выбранных баз данных."""
        return [db_id for db_id, checkbox in self.db_checkboxes.items()
                if checkbox.isChecked()]
