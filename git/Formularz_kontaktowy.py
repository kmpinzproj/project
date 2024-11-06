from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QFormLayout,
    QSplitter, QMainWindow
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from button import StyledButton

class ContactForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formularz Kontaktowy")
        self.setGeometry(300, 100, 800, 500)  # Set a wider width to accommodate both panels

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)

        # Left section (contact form)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Title and subtitle
        title_label = QLabel("Segmentowe. Wyślij zapytanie.")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        subtitle_label = QLabel("Wypełnij formularz kontaktowy. Nasz konsultant skontaktuje się z Tobą.")

        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)

        # Form layout for contact information fields
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.comments_input = QTextEdit()

        form_layout.addRow("Imię i nazwisko*", self.name_input)
        form_layout.addRow("Twój e-mail*", self.email_input)
        form_layout.addRow("Telefon*", self.phone_input)
        form_layout.addRow("Dodatkowe uwagi", self.comments_input)

        # Button layout centered at the bottom
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self.back_button = StyledButton("Cofnij")
        self.submit_button = StyledButton("Wyślij")

        # Add buttons to the button layout
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.submit_button)

        # Adding layouts and widgets to the left layout
        left_layout.addLayout(form_layout)
        left_layout.addLayout(button_layout)  # Add centered button layout

        # Right section (placeholder for 3D view)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        placeholder_label = QLabel("Widok 3D (Placeholder)")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(placeholder_label)

        # Adding left and right widgets to the main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
