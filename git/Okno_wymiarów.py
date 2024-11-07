from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from button import StyledButton


class OknoWymiarow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Ustawienie minimalnego rozmiaru okna

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Configures the main layout and divides it into left and right panels."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left and Right panels
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Ustawienie rozciągania: lewy panel nieco szerszy
        main_layout.setStretch(0, 3)  # Lewy panel
        main_layout.setStretch(1, 2)  # Prawy panel

    def _create_left_panel(self):
        """Creates the left panel with input fields and buttons."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Spacer to push content lower on the panel
        self._add_spacer(left_layout)

        # Title label
        dimensions_label = QLabel("Podaj wymiary")
        dimensions_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(dimensions_label)

        # Input fields with labels
        self._add_input_field(left_layout, "Szerokość", self._create_int_input())
        self._add_input_field(left_layout, "Wysokość", self._create_int_input())

        # Spacer to center input fields vertically
        self._add_spacer(left_layout)

        # Buttons at the bottom
        buttons_layout = QHBoxLayout()
        self.back_button = StyledButton("Cofnij")
        self.accept_button = StyledButton("Akceptuj")
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.accept_button)
        left_layout.addLayout(buttons_layout)

        # Ustaw politykę rozmiaru na Expanding, aby był elastyczny
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return left_widget

    def _create_right_panel(self):
        """Creates the right panel with measurement instructions."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Instruction label
        instruction_label = QLabel(
            "Instrukcja pomiaru:\n"
            "1. Zmierz wysokość i szerokość otworu.\n"
            "2. Zanotuj dokładne wartości.\n"
            "3. Upewnij się, że pomiary są prawidłowe."
        )
        instruction_label.setWordWrap(True)
        right_layout.addWidget(instruction_label)

        # Ustaw politykę rozmiaru, aby prawy panel mógł się elastycznie rozszerzać
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return right_widget

    def _add_input_field(self, layout, label_text, input_field):
        """Adds a labeled input field to the specified layout."""
        label = QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(input_field)

    def _create_int_input(self):
        """Creates an input field with an integer validator."""
        input_field = QLineEdit()
        input_field.setValidator(QIntValidator())
        return input_field

    def _add_spacer(self, layout):
        """Adds a vertical spacer to center content vertically."""
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))