from PySide6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QFrame,
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGraphicsView, QSizePolicy, QListWidget)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from button import StyledButton


class WyborBramy(QMainWindow):
    # Constants for frame size
    FRAME_WIDTH = 390
    FRAME_HEIGHT = 220

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Zachowanie minimalnego rozmiaru

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Grid layout for frames
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        # Frames setup
        self.add_frame("Brama Rozwierana", "Nie wymagają wolnego miejsca wewnątrz garażu oraz wolego naproża. Można zamontować je praktycznie w każdym garażu. Ekonomiczne rozwiązanie za rozsądną cenę.", 0, 0)
        self.add_frame("Brama Roletowa", "Odpowiednie rozwiązanie dla osób, które cenią funkcjonalność. Oszczędność miejsca w garażu i na podjeździe, a zarazem napęd elektryczny w standardzie.", 0, 1)
        self.add_frame("Brama Uchylna", "Prostota , tradycja i nowoczesność. Najczęściej stosowane w nieocieplonych garażach wolnostojących lub w budynkach wielomieszkaniowych.", 1, 0)
        self.add_frame("Brama Segmentowa", "Najbardziej komfortowe rozwiązanie do garażu. Otwierane pionowo w górę oszczędzają miejsce przed i wewnątrz garażu. Ciepłe i ciche polecane do garaży ogrzewanych.", 1, 1)

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

        # Inner frame with graphics view and button
        frame_inner = QFrame(frame)
        horizontal_layout = QHBoxLayout(frame_inner)

        # graphics_view = QListWidget(frame_inner)
        # graphics_view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # horizontal_layout.addWidget(graphics_view)

        button = StyledButton("Wybierz", frame_inner)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        horizontal_layout.addWidget(button)

        vertical_layout.addWidget(frame_inner)
        return frame

    def create_title_label(self, title):
        """Creates a title label with bold styling."""
        label_title = QLabel(title)
        font = QFont()
        font.setBold(True)
        label_title.setFont(font)
        label_title.setStyleSheet("color: rgb(105, 64, 14);")
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label_title

    def create_description_label(self, description):
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
        self.accept_button = StyledButton("Akceptuj")

        # Add buttons with centered alignment
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(self.accept_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(buttons_widget)
        buttons_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)