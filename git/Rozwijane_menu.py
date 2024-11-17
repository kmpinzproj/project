from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QLabel, QHBoxLayout, QGridLayout, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap
import os


class ScrollableMenu(QWidget):
    FIELD_HEIGHT = 100  # Default height for fields

    def __init__(self, gate_type):
        super().__init__()
        self.setWindowTitle("Przewijane menu")
        self.setMinimumWidth(400)

        self.gate_type = gate_type
        self.category_widgets = {}
        self.option_items_by_category = {}
        self.options_layout_by_category = {}

        layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)

        # Load data into content_layout
        options_data = self.load_options_data("options_data.txt")
        if self.gate_type in options_data:
            for field_name, options in options_data[self.gate_type].items():
                field_group = self._create_field_group(field_name, options)
                self.content_layout.addWidget(field_group)
                self.category_widgets[field_name] = field_group
        else:
            no_data_label = QLabel(f"Brak danych dla bramy typu: {self.gate_type}")
            self.content_layout.addWidget(no_data_label)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Monitor resize events of the parent window (Kreator)
        self.installEventFilter(self)

    def load_options_data(self, filename):
        options_data = {}
        current_gate = None

        with open(filename, 'r', encoding='utf-8') as file:
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
        field_layout = QVBoxLayout(field_group)

        header_layout = QHBoxLayout()
        label = QLabel(field_name)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(label)

        toggle_button = self._create_toggle_button()
        header_layout.addWidget(toggle_button, alignment=Qt.AlignRight)

        field_layout.addLayout(header_layout)

        # Check if the field is for color options with images
        if field_name in ["Kolor Standardowy", "Kolor RAL"]:
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

        options_layout.setContentsMargins(5, 5, 5, 5)
        options_layout.setSpacing(10)

        folder_path = os.path.abspath(os.path.join("../jpg", category.replace(" ", "_")))

        option_items = []
        for option in options:
            image_path = os.path.join(folder_path, f"{option}.png")
            option_widget = self._create_image_option(option, image_path)
            option_items.append(option_widget)

        # Store layout and items for the category
        self.option_items_by_category[category] = option_items
        self.options_layout_by_category[category] = options_layout

        # Add widgets to the grid layout
        for index, widget in enumerate(option_items):
            row = index // 3
            column = index % 3
            options_layout.addWidget(widget, row, column)

        return options_widget

    def _create_image_option(self, option_name, image_path):
        option_widget = QWidget()
        layout = QVBoxLayout(option_widget)
        layout.setAlignment(Qt.AlignCenter)

        image_label = QLabel()
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            pixmap = QPixmap("../jpg/placeholder.jpg")  # Default image if not found

        pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)

        text_label = QLabel(option_name)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setFixedWidth(80)
        text_label.setFixedHeight(40)

        layout.addWidget(image_label)
        layout.addWidget(text_label)

        option_widget.setFixedSize(100, 140)
        return option_widget

    def eventFilter(self, source, event):
        """Monitor resize events of the parent (main window) to dynamically update columns."""
        if event.type() == QEvent.Resize:
            self._update_grid_columns()
        return super().eventFilter(source, event)

    def _update_grid_columns(self):
        available_width = self.scroll_area.viewport().width()
        option_width = 100
        spacing = 10

        columns = max(3, available_width // (option_width + spacing))

        for category, option_items in self.option_items_by_category.items():
            layout = self.options_layout_by_category[category]

            # Remove all widgets from the layout
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget:
                    layout.removeWidget(widget)

            # Re-add widgets to the grid layout with the new column count
            for index, widget in enumerate(option_items):
                row = index // columns
                column = index % columns
                layout.addWidget(widget, row, column)

            # Adjust the height of the widget for this category
            self._adjust_widget_height(option_items, columns, layout)

    def _adjust_widget_height(self, option_items, columns, layout):
        total_items = len(option_items)
        rows = (total_items + columns - 1) // columns  # Ceiling division
        option_height = 140
        spacing = 10

        new_height = max(0, rows * (option_height + spacing) - spacing)
        parent_widget = layout.parentWidget()
        parent_widget.setFixedHeight(new_height)
        parent_widget.setVisible(False)  # Force refresh
        parent_widget.setVisible(True)
        parent_widget.updateGeometry()

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
            self._update_grid_columns()
            field_group.setFixedHeight(options_widget.sizeHint().height())
            field_group.updateGeometry()