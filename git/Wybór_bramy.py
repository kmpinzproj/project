from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QFrame, QVBoxLayout,
    QHBoxLayout, QLabel, QSizePolicy
)

from button import StyledButton
import os
import json


class WyborBramy(QMainWindow):
    # Constants for frame size
    FRAME_WIDTH = 390
    FRAME_HEIGHT = 220

    def __init__(self, dimension_view):
        super().__init__()
        self.back_button = None
        self.accept_button = None
        self.dimension_view = dimension_view
        self.setWindowTitle("Wybór bramy")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Zachowanie minimalnego rozmiaru

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Grid layout for frames
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        # Frames setup with dictionary for easier updates
        gates = {
            "Brama Rozwierana": "Nie wymagają wolnego miejsca wewnątrz garażu oraz wolego naproża. Można zamontować je praktycznie w każdym garażu. Ekonomiczne rozwiązanie za rozsądną cenę.",
            "Brama Roletowa": "Odpowiednie rozwiązanie dla osób, które cenią funkcjonalność. Oszczędność miejsca w garażu i na podjeździe, a zarazem napęd elektryczny w standardzie.",
            "Brama Uchylna": "Prostota , tradycja i nowoczesność. Najczęściej stosowane w nieocieplonych garażach wolnostojących lub w budynkach wielomieszkaniowych.",
            "Brama Segmentowa": "Najbardziej komfortowe rozwiązanie do garażu. Otwierane pionowo w górę oszczędzają miejsce przed i wewnątrz garażu. Ciepłe i ciche polecane do garaży ogrzewanych."
        }

        # Dynamically add frames from the gates dictionary
        for index, (title, description) in enumerate(gates.items()):
            row, column = divmod(index, 2)  # Determine row and column
            self.add_frame(title, description, row, column)

        # Button section
        self.setup_buttons(main_layout)

        # Rozciąganie grid layout
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 0)

    def add_frame(self, title, description, row, column):
        """Adds a frame with given title and description to the specified row and column in the grid layout."""
        frame = self.create_inner_frame(title, description)
        self.grid_layout.addWidget(frame, row, column)

    def create_inner_frame(self, title, description):
        """Creates an individual frame for each door type with a title, description, and selection button."""
        frame = QFrame()
        frame.setMinimumSize(QSize(self.FRAME_WIDTH, self.FRAME_HEIGHT))
        frame.setStyleSheet("background-color: rgb(121, 121, 121);")

        vertical_layout = QVBoxLayout(frame)

        # Title setup
        label_title = self.create_title_label(title)
        vertical_layout.addWidget(label_title)

        # Description setup
        label_description = self.create_description_label(description)
        vertical_layout.addWidget(label_description)

        # Inner frame with selection button
        frame_inner = QFrame(frame)
        horizontal_layout = QHBoxLayout(frame_inner)

        button = StyledButton("Wybierz", frame_inner)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.clicked.connect(lambda _, g=title: (self.dimension_view(), self.save_gate_type(g)))  # Connect button to select_gate method
        horizontal_layout.addWidget(button)

        vertical_layout.addWidget(frame_inner)
        return frame

    @staticmethod
    def create_title_label(title):
        """Creates a title label with bold styling."""
        label_title = QLabel(title)
        font = QFont()
        font.setBold(True)
        label_title.setFont(font)
        label_title.setStyleSheet("color: rgb(105, 64, 14);")
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label_title

    @staticmethod
    def create_description_label(description):
        """Creates a description label with word wrapping and styled color."""
        label_description = QLabel(description)
        label_description.setStyleSheet("color: rgb(74,68,61);")
        label_description.setWordWrap(True)
        return label_description

    def setup_buttons(self, layout):
        """Sets up the bottom navigation buttons."""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.back_button = StyledButton("Cofnij")

        # Add buttons with centered alignment
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(buttons_widget)
        buttons_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # def select_gate(self, gate_type):
    #     """Calls the provided function to save the selected gate type and closes the view."""
    #     self.set_gate_type_func(gate_type)
    #     self.close()

    @staticmethod
    def save_gate_type(gate_type):
        """
        Saves the gate type to the JSON file. Creates the file if it doesn't exist.
        """
        file_path = "selected_options.json"
        try:
            # Sprawdź, czy plik istnieje; jeśli nie, utwórz go z pustym słownikiem
            if not os.path.isfile(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump({}, file, ensure_ascii=False, indent=4)

            # Załaduj istniejące dane z pliku
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Zapisz typ bramy
            data["gate_type"] = gate_type

            # Zapisz zaktualizowane dane do pliku
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Zapisano typ bramy: {gate_type} do pliku {file_path}")
        except OSError as e:
            print(f"Wystąpił błąd podczas operacji na pliku: {e}")
        except Exception as e:
            print(f"Wystąpił niespodziewany błąd: {e}")