from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QPushButton, QCheckBox,
    QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt


class ScrollableMenu(QWidget):
    # Constants for layout
    FIELD_HEIGHT = 100  # Default height for fields

    def __init__(self, gate_type):
        super().__init__()
        self.setWindowTitle("Przewijane menu")
        self.resize(400, 600)

        # Typ bramy dla załadowania odpowiednich opcji
        self.gate_type = gate_type

        # Ustawienie głównego layoutu
        layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Kontener na pola opcji
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Wczytaj i utwórz pola na podstawie danych dla wybranej bramy
        options_data = self.load_options_data("options_data.txt")
        if self.gate_type in options_data:
            for field_name, options in options_data[self.gate_type].items():
                field_group = self._create_field_group(field_name, options)
                content_layout.addWidget(field_group)
        else:
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

                if line.startswith('[') and line.endswith(']'):
                    current_gate = line[1:-1]
                    options_data[current_gate] = {}
                elif current_gate:
                    field_name, options = self._parse_line(line)
                    if field_name:
                        options_data[current_gate].setdefault(field_name, {}).update(options)

        return options_data

    @staticmethod
    def _parse_line(line):
        """Parses a line of the options file and returns a field name and options dictionary."""
        if ': ' not in line:
            return None, None

        field_name, options = line.split(': ', 1)
        if field_name in ["Kolor Standardowy", "Kolor RAL"]:
            color_type = "Kolor Standardowy" if field_name == "Kolor Standardowy" else "Kolor RAL"
            options_dict = {color_type: options.split(", ")}
        else:
            options_dict = {field_name: options.split(", ")}

        return field_name.split(" ")[0] if "Kolor" in field_name else field_name, options_dict

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

        # Toggle button
        toggle_button = self._create_toggle_button()
        header_layout.addWidget(toggle_button, alignment=Qt.AlignRight)
        field_layout.addLayout(header_layout)

        # Opcje dla pola (standardowe lub kolor)
        options_widget = self._create_color_options_widget(options) if "Kolor" in field_name else self._create_options_widget(options)
        options_widget.setVisible(False)
        field_layout.addWidget(options_widget)

        # Toggle visibility on button click
        toggle_button.clicked.connect(lambda: self.toggle_options(field_group, options_widget, toggle_button))

        return field_group

    @staticmethod
    def _create_color_options_widget(options):
        """Creates a nested options widget for color selection."""
        color_widget = QWidget()
        color_layout = QVBoxLayout(color_widget)

        for color_type, colors in options.items():
            group_box = QGroupBox(color_type)
            group_layout = QVBoxLayout(group_box)
            for color in colors:
                group_layout.addWidget(QCheckBox(color))
            color_layout.addWidget(group_box)

        return color_widget

    @staticmethod
    def _create_toggle_button():
        """Creates a toggle button for expanding/collapsing options."""
        button = QPushButton("↓")
        button.setFixedSize(24, 24)
        button.setFlat(True)
        return button

    @staticmethod
    def _create_options_widget(options):
        """Creates a widget with checkboxes for the provided options."""
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        for option in options:
            checkbox = QCheckBox(option)
            options_layout.addWidget(checkbox)

        return options_widget

    def toggle_options(self, field_group, options_widget, toggle_button):
        """Toggles the visibility of options and adjusts the group height."""
        is_visible = options_widget.isVisible()
        options_widget.setVisible(not is_visible)
        field_group.setFixedHeight(self.FIELD_HEIGHT if is_visible else self.FIELD_HEIGHT + options_widget.sizeHint().height())
        toggle_button.setText("↓" if is_visible else "↑")