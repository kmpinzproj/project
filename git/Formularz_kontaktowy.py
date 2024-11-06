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
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 800, 600)

        # Setup the main interface
        self.setup_ui()

    def setup_ui(self):
        # Central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left and Right panels
        navigation_panel = self.create_navigation_panel()
        view_panel = self.create_view_panel()

        main_layout.addWidget(navigation_panel)
        main_layout.addWidget(view_panel)

    def create_navigation_panel(self):
        # Define navigation panel components
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title and subtitle
        title_label = QLabel("Segmentowe. Wyślij zapytanie.")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        subtitle_label = QLabel("Wypełnij formularz kontaktowy. Nasz konsultant skontaktuje się z Tobą.")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        # Form layout for contact information fields
        form_layout = QFormLayout()
        name_input = QLineEdit()
        email_input = QLineEdit()
        phone_input = QLineEdit()
        comments_input = QTextEdit()

        form_layout.addRow("Imię i nazwisko*", name_input)
        form_layout.addRow("Twój e-mail*", email_input)
        form_layout.addRow("Telefon*", phone_input)
        form_layout.addRow("Dodatkowe uwagi", comments_input)

        # Button layout centered at the bottom
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        # Define buttons
        self.back_button = QPushButton("Cofnij")
        self.submit_button = QPushButton("Wyślij")

        # Add buttons to the button layout
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.submit_button)

        # Adding layouts and widgets to the left layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)  # Add centered button layout

        return panel

    def create_view_panel(self):
        # Define view panel (for 3D view) components here
        panel = QWidget()
        layout = QVBoxLayout(panel)
        placeholder_label = QLabel("Widok 3D (Placeholder)")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setFont(QFont("Arial", 12, QFont.Bold))

        layout.addWidget(placeholder_label)

        return panel