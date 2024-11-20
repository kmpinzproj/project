from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from button import StyledButton
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
import json
import os


class OknoWymiarow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

        self.dimensions = {}  # Zmienna do przechowywania wymiarów

        # Initialize UI
        self._setup_ui()

        # Load dimensions from file if available
        self.load_dimensions_from_file()


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

        main_layout.setStretch(0, 3)  # Left panel is wider
        main_layout.setStretch(1, 2)  # Right panel

    def _create_left_panel(self):
        """Creates the left panel with input fields and navigation buttons."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self._add_spacer(left_layout)

        # Title label
        dimensions_label = QLabel("Podaj wymiary")
        dimensions_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(dimensions_label)

        # Input fields for dimensions
        self.width_input = self._create_int_input("Szerokość", left_layout, 2200, 9999)
        self.height_input = self._create_int_input("Wysokość", left_layout, 2000, 9999)

        # Podłącz sygnały `textChanged` do walidacji
        self.width_input.textChanged.connect(self.validate_inputs)
        self.height_input.textChanged.connect(self.validate_inputs)

        # Spacer to center input fields vertically
        self._add_spacer(left_layout)

        # Add navigation buttons at the bottom
        self._add_navigation_buttons(left_layout)

        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return left_widget

    @staticmethod
    def _create_right_panel():
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

        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return right_widget

    @staticmethod
    def _create_int_input(label_text, layout, min_value, max_value):
        """Creates an input field with an integer validator and adds it to the specified layout with a label."""
        label = QLabel(label_text)
        input_field = QLineEdit()

        # Walidator ograniczający wartości do podanego zakresu
        validator = QIntValidator(min_value, max_value)
        input_field.setValidator(validator)

        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def _add_navigation_buttons(self, layout):
        """Adds navigation buttons to the layout at the bottom of the panel."""
        buttons_layout = QHBoxLayout()
        self.back_button = StyledButton("Cofnij")
        self.accept_button = StyledButton("Akceptuj")

        # Początkowo przycisk „Akceptuj” jest wyłączony
        self.accept_button.setEnabled(False)

        # Obsługa kliknięcia przycisku „Akceptuj”
        self.accept_button.clicked.connect(self.save_dimensions)

        # Add buttons with centered alignment
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.accept_button)
        layout.addLayout(buttons_layout)

    @staticmethod
    def _add_spacer(layout):
        """Adds a vertical spacer to center content vertically."""
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def save_dimensions(self):
        """Reads the dimensions from input fields and saves them to self.dimensions and the JSON file."""
        width = self.width_input.text()
        height = self.height_input.text()

        if width.isdigit() and height.isdigit():
            self.dimensions['width'] = int(width)
            self.dimensions['height'] = int(height)

            # Zapisz wymiary do pliku JSON
            self.save_dimensions_to_file()


    def validate_inputs(self):
        """Enable or disable the accept button based on whether the inputs are filled and valid."""
        width = self.width_input.text()
        height = self.height_input.text()

        # Sprawdzamy, czy oba pola są wypełnione i czy wartości są w odpowiednim zakresie
        if width.isdigit() and height.isdigit():  # Dodatkowa weryfikacja, czy są to liczby
            width = int(width)
            height = int(height)

            if width >= 2200 and height >= 2000:
                self.accept_button.setEnabled(True)
                return

        # Jeśli wartości są nieprawidłowe, przycisk pozostaje wyłączony
        self.accept_button.setEnabled(False)

    def save_dimensions_to_file(self, file_path="selected_options.json"):
        """Saves the gate dimensions to a JSON file."""
        try:
            # Ensure the file exists; if not, create an empty JSON structure
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump({}, file, ensure_ascii=False, indent=4)

            # Load existing data from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Update the dimensions in the file
            data['dimensions'] = {
                'width': self.dimensions.get('width', 0),
                'height': self.dimensions.get('height', 0)
            }

            # Save the updated data back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print(f"Wymiary zostały zapisane: {data['dimensions']}")

        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania wymiarów do pliku: {e}")

    def load_dimensions_from_file(self, file_path="selected_options.json"):
        """Loads dimensions from the JSON file and updates the input fields."""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                dimensions = data.get('dimensions', {})
                self.dimensions = dimensions

                # Update input fields with loaded dimensions
                if 'width' in dimensions:
                    self.width_input.setText(str(dimensions['width']))
                if 'height' in dimensions:
                    self.height_input.setText(str(dimensions['height']))

                print(f"Wczytano wymiary: {dimensions}")

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Błąd podczas wczytywania wymiarów: {e}")
        else:
            print(f"Plik {file_path} nie istnieje. Wymiary nie zostały wczytane.")