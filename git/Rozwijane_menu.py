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

        # Przechowujemy typ bramy, aby załadować odpowiednie opcje
        self.gate_type = "Brama Segmentowa"

        # Ustawienie głównego layoutu
        layout = QVBoxLayout(self)

        # Tworzenie scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Kontener na pola
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Wczytaj dane z pliku
        options_data = self.load_options_data("options_data.txt")

        # Tworzenie pól na podstawie danych dla wybranej bramy
        if self.gate_type in options_data:
            for field_name, options in options_data[self.gate_type].items():
                field_group = self._create_field_group(field_name, options)
                content_layout.addWidget(field_group)
        else:
            # W przypadku braku danych dla wybranej bramy wyświetl komunikat
            no_data_label = QLabel(f"Brak danych dla bramy typu: {self.gate_type}")
            content_layout.addWidget(no_data_label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

    def load_options_data(self, filename):
        """Wczytuje dane z pliku txt i zwraca jako słownik z opcjami dla różnych bram."""
        options_data = {}
        current_gate = None

        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Rozpoznaj nową bramę na podstawie nagłówka w nawiasach kwadratowych
                if line.startswith('[') and line.endswith(']'):
                    current_gate = line[1:-1]  # Nazwa bramy
                    options_data[current_gate] = {}
                elif current_gate:
                    # Rozdziel kategorię opcji i wartości
                    if line.startswith("Kolor Standardowy"):
                        field_name, colors = line.split(": ", 1)
                        options_data[current_gate].setdefault("Kolor", {}).update(
                            {"Kolor Standardowy": colors.split(", ")})
                    elif line.startswith("Kolor RAL"):
                        field_name, colors = line.split(": ", 1)
                        options_data[current_gate].setdefault("Kolor", {}).update({"Kolor RAL": colors.split(", ")})
                    elif ': ' in line:
                        field_name, options = line.split(': ', 1)
                        options_data[current_gate][field_name] = options.split(', ')

        return options_data

    def _create_field_group(self, field_name, options):
        """Creates a group of options with a toggle button and checkboxes, with support for nested options."""
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

        # Tworzenie zagnieżdżonej struktury dla opcji Kolor
        if "Kolor" in field_name:
            options_widget = self._create_color_options_widget(options)
        else:
            options_widget = self._create_options_widget(options)

        options_widget.setVisible(False)
        field_layout.addWidget(options_widget)

        # Toggle visibility of options on button click
        toggle_button.clicked.connect(lambda: self.toggle_options(field_group, options_widget, toggle_button))

        return field_group

    def _create_color_options_widget(self, options):
        """Creates a nested options widget for color selection."""
        color_widget = QWidget()
        color_layout = QVBoxLayout(color_widget)

        # Dodanie opcji "Kolor Standardowy"
        standard_group = QGroupBox("Kolor Standardowy")
        standard_layout = QVBoxLayout(standard_group)
        for color in options.get("Kolor Standardowy", []):
            standard_layout.addWidget(QCheckBox(color))
        color_layout.addWidget(standard_group)

        # Dodanie opcji "Kolor RAL"
        ral_group = QGroupBox("Kolor RAL")
        ral_layout = QVBoxLayout(ral_group)
        for color in options.get("Kolor RAL", []):
            ral_layout.addWidget(QCheckBox(color))
        color_layout.addWidget(ral_group)

        return color_widget

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