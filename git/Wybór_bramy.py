from PySide6.QtCore import QCoreApplication, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QMainWindow, QWidget, QFormLayout, QFrame,
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGraphicsView, QMenuBar, QStatusBar)
from button import StyledButton


class WyborBramy(QMainWindow):
    # Constants for frame size
    FRAME_WIDTH = 401
    FRAME_HEIGHT = 231

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Form layout setup
        self.form_layout = QFormLayout()
        main_layout.addLayout(self.form_layout)

        # Frames setup
        self.add_frame("Brama Rozwierana", "Nie wymagają wolnego miejsca wewnątrz garażu oraz wolnego naproża...", 0,
                       QFormLayout.LabelRole)
        self.add_frame("Brama Roletowa", "Odpowiednie rozwiązanie dla osób, które cenią funkcjonalność...", 0,
                       QFormLayout.FieldRole)
        self.add_frame("Brama Uchylna", "Prostota, tradycja i nowoczesność...", 1, QFormLayout.LabelRole)
        self.add_frame("Brama Segmentowa", "Najbardziej komfortowe rozwiązanie do garażu...", 1, QFormLayout.FieldRole)

        # Button section
        self.setup_buttons(main_layout)

    def add_frame(self, title, description, row, role):
        """Adds a frame with given title and description to the specified row and role."""
        frame = self.create_inner_frame(title, description)
        self.form_layout.setWidget(row, role, frame)

    def create_inner_frame(self, title, description):
        """Creates an individual frame for each door type with a title, description, and selection button."""
        frame = QFrame()
        frame.setMinimumSize(QSize(self.FRAME_WIDTH, self.FRAME_HEIGHT))
        frame.setMaximumSize(QSize(self.FRAME_WIDTH, self.FRAME_HEIGHT))
        frame.setStyleSheet("background-color: rgb(255, 249, 218);")

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

        graphics_view = QGraphicsView(frame_inner)
        horizontal_layout.addWidget(graphics_view)

        button = QPushButton("Wybierz", frame_inner)
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
        buttons_layout.addWidget(self.back_button,
                                 alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(self.accept_button,
                                 alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(buttons_widget)