from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel
)
from PySide6.QtGui import QPixmap
from Rozwijane_menu import ScrollableMenu
from button import StyledButton
import os


class Kreator(QMainWindow):
    LEFT_PANEL_WIDTH = 400
    IMAGE_WIDGET_MIN_SIZE = 400  # Minimum size for image widget

    def __init__(self, gate_type, image_path="cube_render.png"):
        super().__init__()
        self.gate_type = gate_type
        # Poprawiona ścieżka
        self.image_path = os.path.abspath(image_path) if image_path else None
        self.setWindowTitle(f"Kreator - {self.gate_type}")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

        # Initialize UI
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the main layout and divides it into left and right panels."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Tworzenie lewego i prawego panelu
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        # Dodaj panele do głównego układu
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Ustaw proporcje rozciągania dla lewego i prawego panelu
        main_layout.setStretch(0, 1)  # Lewy panel
        main_layout.setStretch(1, 1)  # Prawy panel, równomierna proporcja do lewego panelu

    def _create_left_panel(self):
        """Creates the left panel with the scrollable menu based on gate type."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Add scrollable navigation menu
        navigation_menu = ScrollableMenu(self.gate_type)
        navigation_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ustawienie na elastyczny rozmiar
        left_layout.addWidget(navigation_menu)

        return left_widget

    def _create_right_panel(self):
        """Creates the right panel with QLabel for image display and navigation buttons."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # QLabel widget for image display
        image_widget = self._create_image_widget()
        right_layout.addWidget(image_widget)

        # Navigation buttons at the bottom
        buttons_widget = self._create_navigation_buttons()
        right_layout.addWidget(buttons_widget)

        return right_widget

    def _create_image_widget(self):
        """Creates and configures the QLabel widget for image display."""
        image_label = QLabel()
        image_label.setObjectName("imageLabel")
        image_label.setMinimumSize(self.IMAGE_WIDGET_MIN_SIZE, self.IMAGE_WIDGET_MIN_SIZE)
        image_label.setAlignment(Qt.AlignCenter)  # Wyśrodkowanie obrazu

        # Ładowanie obrazka
        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)

            if not pixmap.isNull():
                # Dopasowanie obrazu z zachowaniem proporcji
                scaled_pixmap = pixmap.scaled(
                    self.IMAGE_WIDGET_MIN_SIZE,
                    self.IMAGE_WIDGET_MIN_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("Nie znaleziono obrazka")
            image_label.setAlignment(Qt.AlignCenter)

        return image_label

    def _create_navigation_buttons(self):
        """Creates a widget with 'Back' and 'Save' buttons."""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        # Create Back and Save buttons
        self.back_button = StyledButton("Cofnij")
        self.save_button = StyledButton("Zapisz")

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.save_button)

        # Remove margins and spacing for navigation buttons
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        return buttons_widget