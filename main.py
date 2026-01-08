import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow

def main():
    # Создаем приложение PyQt
    app = QApplication(sys.argv)

    # Создаем и показываем главное окно
    window = MainWindow()

    app.setApplicationName("PSQL Mock Creator")
    app.setWindowIcon(window.get_app_icon())

    window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()