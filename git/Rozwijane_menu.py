from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QLabel, QHBoxLayout, QGridLayout, QCheckBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os


class ScrollableMenu(QWidget):
    FIELD_HEIGHT = 100  # Default height for fields
    def __init__(self, gate_type):
        super().__init__()
        self.setWindowTitle("Przewijane menu")
        self.resize(400, 600)
        self.setMinimumWidth(400)

        self.gate_type = gate_type
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

        # Dodanie danych do content_layout
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
                    if ': ' in line:
                        field_name, options = line.split(': ', 1)
                        options_data[current_gate][field_name] = options.split(', ')

        return options_data

    def _create_field_group(self, field_name, options):
        field_group = QGroupBox()
        field_group.setFixedHeight(self.FIELD_HEIGHT)
        field_layout = QVBoxLayout(field_group)

        header_layout = QHBoxLayout()
        label = QLabel(field_name)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(label)

        toggle_button = self._create_toggle_button()
        header_layout.addWidget(toggle_button, alignment=Qt.AlignRight)

        field_layout.addLayout(header_layout)

        if field_name == "Układ wypełnienia":
            options_widget = self._create_image_options_widget(field_name, options)
        else:
            options_widget = self._create_options_widget(options)

        options_widget.setVisible(False)
        field_layout.addWidget(options_widget)

        toggle_button.clicked.connect(lambda: self.toggle_options(field_group, options_widget, toggle_button))

        return field_group

    def _create_image_options_widget(self, category, options):
        options_widget = QWidget()
        options_layout = QGridLayout(options_widget)

        # Ustawienie szerokości siatki na sztywno
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(5)  # Odstęp między elementami

        folder_path = os.path.abspath(os.path.join("../jpg", category.replace(" ", "_")))

        for i, option in enumerate(options):
            image_path = os.path.join(folder_path, f"{option}.png")
            option_widget = self._create_image_option(option, image_path)
            options_layout.addWidget(option_widget, i // 3, i % 3)  # Siatka o szerokości 3

        options_widget.setFixedWidth(325)  # Ustaw szerokość na całą siatkę
        return options_widget

    def _create_image_option(self, option_name, image_path):
        option_widget = QWidget()
        layout = QVBoxLayout(option_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Kontener dla obrazka
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setAlignment(Qt.AlignCenter)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Obrazek
        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            pixmap = QPixmap("../jpg/placeholder.jpg")

        # Ustawienie rozmiaru obrazka bez zmiany proporcji
        pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)

        image_layout.addWidget(image_label)
        image_container.setFixedSize(80, 80)  # Stały rozmiar kontenera dla obrazka
        layout.addWidget(image_container)

        # Tekst
        text_label = QLabel(option_name)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setFixedWidth(80)
        text_label.setFixedHeight(
            40)  # Stała wysokość dla tekstu, aby zawijał się w dwóch wierszach bez wpływu na obrazek

        layout.addWidget(text_label)

        # Ustawienie stałego rozmiaru widgetu opcji
        option_widget.setFixedSize(100, 140)  # Dopasowanie rozmiaru do większych obrazków i tekstu
        return option_widget

    def _create_options_widget(self, options):
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        for option in options:
            checkbox = QCheckBox(option)
            options_layout.addWidget(checkbox)

        return options_widget

    def _create_toggle_button(self):
        button = QPushButton("↓")
        button.setFixedSize(24, 24)
        button.setFlat(True)
        return button

    def toggle_options(self, field_group, options_widget, toggle_button):
        if options_widget.isVisible():
            options_widget.setVisible(False)
            field_group.setFixedHeight(self.FIELD_HEIGHT)
            toggle_button.setText("↓")
        else:
            options_widget.setVisible(True)
            expanded_height = self.FIELD_HEIGHT + options_widget.sizeHint().height()
            field_group.setFixedHeight(expanded_height)
            toggle_button.setText("↑")