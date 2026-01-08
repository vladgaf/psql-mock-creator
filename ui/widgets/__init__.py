"""
Виджеты (QWidget наследники) для главного окна.
"""

from .connection_config_widget import ConnectionConfigWidget
from .console_output_widget import ConsoleOutputWidget
from .control_buttons_widget import ControlButtonsWidget
from .database_selection_widget import DatabaseSelectionWidget

__all__ = [
    'ConnectionConfigWidget',
    'DatabaseSelectionWidget',
    'ControlButtonsWidget',
    'ConsoleOutputWidget',
]
