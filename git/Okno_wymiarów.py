from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel,
                               QLineEdit, QVBoxLayout, QHBoxLayout,
                               QPushButton,QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from button import StyledButton

class OknoWymiarow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 800, 600)

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Splitter to divide the window into left and right sections
        # splitter = QSplitter(Qt.Horizontal)

        g_widget = QWidget()
        g_layout = QHBoxLayout(g_widget)

        # Left side layout (Inputs and buttons)
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)

        # Spacer to push content to vertical center
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Label for "Podaj wymiary" and input fields
        dimensions_label = QLabel("Podaj wymiary")
        dimensions_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(dimensions_label)

        # Width input
        width_label = QLabel("Szerokość")
        self.width_input = QLineEdit()
        self.width_input.setValidator(QIntValidator())
        left_layout.addWidget(width_label)
        left_layout.addWidget(self.width_input)

        # Height input
        height_label = QLabel("Wysokość")
        self.height_input = QLineEdit()
        self.height_input.setValidator(QIntValidator())
        left_layout.addWidget(height_label)
        left_layout.addWidget(self.height_input)

        # Spacer to keep the input fields centered, buttons remain at the bottom
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons (Cofnij and Akceptuj) side by side at the bottom
        buttons_layout = QHBoxLayout()
        self.back_button = StyledButton("Cofnij")
        self.accept_button = StyledButton("Akceptuj")
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.accept_button)
        left_layout.addLayout(buttons_layout)

        # Add left widget to splitter
        g_layout.addWidget(left_widget)

        # Right side layout (Measurement instructions)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        instruction_label = QLabel(
            "Instrukcja pomiaru:\n1. Zmierz wysokość i szerokość otworu.\n2. Zanotuj dokładne wartości.\n3. Upewnij się, że pomiary są prawidłowe.")
        instruction_label.setWordWrap(True)
        right_layout.addWidget(instruction_label)

        # Add right widget to splitter
        g_layout.addWidget(right_widget)

        # Set splitter as the main layout in central widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(g_widget)