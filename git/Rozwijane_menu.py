from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QPushButton, QCheckBox,
    QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt


class ScrollableMenu(QWidget):
    # Constants for layout
    FIELD_HEIGHT = 100  # Default height for fields

    def __init__(self):
        super().__init__()

        # Główna konfiguracja okna
        self.setWindowTitle("Przewijane menu")
        self.resize(400, 600)

        # Ustawienie głównego layoutu
        layout = QVBoxLayout(self)

        # Tworzenie scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Kontener na pola
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Lista pól z opcjami
        options_data = {
            "Układ wypełnienia": ["Pionowe", "Poziome", "Jodełka w górę"],
            "Kolor": ["Biały", "Brąz", "Złoty dąb", "Orzech", "Mahoń", "Dąb antyczny", "Dąb ciemny"],
            "Sposób otwierania drzwi": ["Ręczne", "Automatyczne"],
            "Przeszklenia": ["Tak", "Okna poziome", "Okna pionowe"],
            "Drzwi przejściowe": ["Tak"],
            "Opcje dodatkowe": ["Rygiel trzypunktowy", "Kratki wentylacyjne", "Dodatkowy rygiel"]
        }

        # Tworzenie pól na podstawie danych
        for field_name, options in options_data.items():
            field_group = self._create_field_group(field_name, options)
            content_layout.addWidget(field_group)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

    def _create_field_group(self, field_name, options):
        """Creates a group of options with a toggle button and checkboxes."""
        field_group = QGroupBox()
        field_group.setFixedHeight(self.FIELD_HEIGHT)
        field_layout = QVBoxLayout(field_group)

        # Header with label and toggle button
        header_layout = QHBoxLayout()
        label = QLabel(field_name)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(label)

        # Toggle button setup
        toggle_button = self._create_toggle_button()
        header_layout.addWidget(toggle_button, alignment=Qt.AlignRight)

        # Add header and options
        field_layout.addLayout(header_layout)

        # Hidden options widget
        options_widget = self._create_options_widget(options)
        options_widget.setVisible(False)
        field_layout.addWidget(options_widget)

        # Toggle visibility of options on button click
        toggle_button.clicked.connect(lambda: self.toggle_options(field_group, options_widget, toggle_button))

        return field_group

    def _create_toggle_button(self):
        """Creates a toggle button for expanding/collapsing options."""
        button = QPushButton("↓")
        button.setFixedSize(24, 24)
        button.setFlat(True)
        return button

    def _create_options_widget(self, options):
        """Creates a widget with checkboxes for the provided options."""
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        for option in options:
            checkbox = QCheckBox(option)
            options_layout.addWidget(checkbox)

        return options_widget

    def toggle_options(self, field_group, options_widget, toggle_button):
        """Toggles the visibility of options and adjusts the group height."""
        if options_widget.isVisible():
            options_widget.setVisible(False)
            field_group.setFixedHeight(self.FIELD_HEIGHT)
            toggle_button.setText("↓")
        else:
            options_widget.setVisible(True)
            expanded_height = self.FIELD_HEIGHT + options_widget.sizeHint().height()
            field_group.setFixedHeight(expanded_height)
            toggle_button.setText("↑")