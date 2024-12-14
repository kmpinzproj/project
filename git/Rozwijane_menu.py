from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QLabel, QHBoxLayout, QGridLayout, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap, QPalette, QColor
import os


class ScrollableMenu(QWidget):
    FIELD_HEIGHT = 100  # Default height for collapsed fields
    OPTION_WIDGET_SIZE = (100, 140)  # Width and height of option widgets

    def __init__(self, gate_type):
        super().__init__()
        self.setWindowTitle("Przewijane menu")
        self.setMinimumWidth(400)
        self.setObjectName("rozwijane_menu")


        self.gate_type = gate_type
        self.category_widgets = {}  # Store field group, options widget, and toggle button for each category
        self.option_items_by_category = {}  # Store option items per category
        self.options_layout_by_category = {}  # Store grid layouts per category
        self.selected_options = {}  # Track selected options by category
        self.last_selected_color = None  # Przechowuje ostatnio zaznaczoną opcję z dwóch kategorii

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)

        options_data = self.load_options_data("../resources/options_data.txt")
        if self.gate_type in options_data:
            for field_name, options in options_data[self.gate_type].items():
                self.content_layout.addWidget(self._create_field_group(field_name, options))
        else:
            no_data_label = QLabel(f"Brak danych dla bramy typu: {self.gate_type}")
            self.content_layout.addWidget(no_data_label)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        self.installEventFilter(self)  # Monitor resize events for dynamic updates

    def _create_field_group(self, field_name, options):
        """Create a field group for a category."""
        field_group = QGroupBox()
        field_layout = QVBoxLayout(field_group)

        # Header with toggle button
        header_layout = QHBoxLayout()
        header_label = QLabel(field_name)
        header_label.setObjectName("title")
        header_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(header_label)

        toggle_button = self._create_toggle_button()
        header_layout.addWidget(toggle_button, alignment=Qt.AlignRight)

        field_layout.addLayout(header_layout)

        # Options widget
        if field_name in ["Kolor standardowy", "Kolor RAL", "Układ wypełnienia", "Wysokość profili",
                          "Struktura powierzchni", "Rodzaj przetłoczenia", "Przeszklenia", "Klamka do bramy"]:
            options_widget = self._create_image_options_widget(field_name, options)
        else:
            options_widget = self._create_checkbox_options_widget(options, field_name)

        options_widget.setVisible(False)
        field_layout.addWidget(options_widget)

        # Store field group components
        self.category_widgets[field_name] = {
            "field_group": field_group,
            "options_widget": options_widget,
            "toggle_button": toggle_button,
        }

        # Set the initial fixed height to FIELD_HEIGHT
        field_group.setFixedHeight(self.FIELD_HEIGHT)

        # Connect toggle button
        toggle_button.clicked.connect(lambda: self.toggle_options(field_name))
        return field_group

    def _create_image_options_widget(self, category, options):
        """Create a widget with grid layout for image-based options."""
        options_widget = QWidget()
        options_layout = QGridLayout(options_widget)

        options_layout.setContentsMargins(5, 5, 5, 5)
        options_layout.setSpacing(10)

        folder_path = os.path.abspath(os.path.join("../jpg", category.replace(" ", "_")))
        option_items = []

        for option in options:
            image_path = os.path.join(folder_path, f"{option}.png")
            option_widget = self._create_image_option(option, image_path, category)
            option_items.append(option_widget)

        # Store layout and items for this category
        self.option_items_by_category[category] = option_items
        self.options_layout_by_category[category] = options_layout

        # **Force one column for "Przeszklenia"**
        if category == "Przeszklenia":
            self._populate_grid_layout(option_items, options_layout, columns=1)
        else:
            self._populate_grid_layout(option_items, options_layout, columns=3)

        return options_widget

    def _create_image_option(self, option_name, image_path, category):
        """Create a single image option widget with selectable functionality and centered text."""
        option_widget = QWidget()
        layout = QVBoxLayout(option_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # Image
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            pixmap = QPixmap("../jpg/placeholder.jpg")

        # Check for specific category to adjust the size
        if category == "Przeszklenia":
            image_label.setPixmap(pixmap.scaled(303, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_label.setFixedSize(303, 60)
        else:
            image_label.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_label.setFixedSize(70, 70)

        image_label.setAlignment(Qt.AlignCenter)
        image_label.setObjectName("image_label")

        # Text
        text_label = QLabel(option_name)
        text_label.setWordWrap(True)
        text_label.setObjectName("text_label")

        # Dostosowanie wyrównania dla kategorii "Przeszklenia"
        if category == "Przeszklenia":
            text_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            text_label.setFixedWidth(303)  # Dostosuj szerokość do przeszklenia
        else:
            text_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            text_label.setMaximumWidth(70)

        text_label.setFixedHeight(40)
        layout.addWidget(image_label)
        layout.addWidget(text_label)

        if category == "Przeszklenia":
            option_widget.setFixedSize(303, 120)  # Full width for przeszklenia
        else:
            option_widget.setFixedSize(self.OPTION_WIDGET_SIZE[0], 120)

        option_widget.mousePressEvent = lambda event: self._on_option_click(category, image_label)

        return option_widget

    def _on_option_click(self, category, image_label):
        """Handle click on an image option."""
        # Zainicjuj zmienną, aby była dostępna w całej funkcji
        selected_text = None

        # Sprawdź, czy kliknięty obrazek jest już zaznaczony
        if image_label.styleSheet() == "border: 5px solid green; padding: 0px; margin: 0px;":
            # Usuń zaznaczenie
            image_label.setStyleSheet("border: none; padding: 0px; margin: 0px;")
            # Usuń zaznaczenie w self.selected_options
            self.selected_options.pop(category, None)
        else:
            # Usuń zaznaczenie poprzednich opcji w tej samej kategorii
            for option_widget in self.option_items_by_category.get(category, []):
                img_label = option_widget.findChild(QLabel, "image_label")
                if img_label:
                    img_label.setStyleSheet("border: none; padding: 0px; margin: 0px;")

            # Specjalne zachowanie dla pól "Kolor standardowy" i "Kolor RAL"
            if category in ["Kolor standardowy", "Kolor RAL"]:
                for color_category in ["Kolor standardowy", "Kolor RAL"]:
                    if color_category in self.category_widgets:
                        field_group = self.category_widgets[color_category]["field_group"]
                        field_group.setStyleSheet("")  # Usuń czerwone obramowanie

                    if color_category != category:
                        for option_widget in self.option_items_by_category.get(color_category, []):
                            img_label = option_widget.findChild(QLabel, "image_label")
                            if img_label:
                                img_label.setStyleSheet("border: none; padding: 0px; margin: 0px;")
                        self.selected_options.pop(color_category, None)
            else:
                if category in self.category_widgets:
                    field_group = self.category_widgets[category]["field_group"]
                    field_group.setStyleSheet("")

            # Zaznacz klikniętą opcję
            image_label.setStyleSheet("border: 5px solid green; padding: 0px; margin: 0px;")

            # Pobierz tekst opcji
            parent_widget = image_label.parent()
            text_label = parent_widget.findChild(QLabel, "text_label")
            selected_text = text_label.text() if text_label else None

            if selected_text:
                self.selected_options[category] = selected_text

        # Zaktualizuj zaznaczoną opcję
        if selected_text:
            self.selected_options[category] = selected_text

    def _create_checkbox_options_widget(self, options, category):
        """Create a widget with checkboxes for options with single selection per category."""
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        category_checkboxes = []  # Store references to checkboxes in this category

        for option in options:
            checkbox = QCheckBox(option)
            checkbox.toggled.connect(lambda state, cb=checkbox: self._on_checkbox_click(category, cb))
            options_layout.addWidget(checkbox)
            category_checkboxes.append(checkbox)

        # Store checkboxes for this category using the category name as key
        self.option_items_by_category[category] = category_checkboxes

        return options_widget

    def _on_checkbox_click(self, category, clicked_checkbox):
        """Handle checkbox clicks. Allow multiple selection for specific categories."""
        if category == "Opcje dodatkowe":
            # Dla "Opcje dodatkowe" zapisuj stan każdego checkboxa
            selected_options = [
                checkbox.text()
                for checkbox in self.option_items_by_category[category]
                if checkbox.isChecked()
            ]
            self.selected_options[category] = selected_options
        else:
            # Dla innych kategorii zachowaj jedno zaznaczenie
            if clicked_checkbox.isChecked():
                # Odznacz wszystkie inne checkboxy w tej kategorii
                for checkbox in self.option_items_by_category[category]:
                    if checkbox != clicked_checkbox:
                        checkbox.blockSignals(True)
                        checkbox.setChecked(False)
                        checkbox.blockSignals(False)

                # Zaktualizuj wybraną opcję
                self.selected_options[category] = clicked_checkbox.text()

                # Usuń czerwoną ramkę, jeśli poprawnie zaznaczono
                if category in self.category_widgets:
                    field_group = self.category_widgets[category]["field_group"]
                    field_group.setStyleSheet("")  # Usuń stylizację (przywróć domyślny wygląd)
            else:
                # Usuń opcję z zaznaczeń, jeśli checkbox został odznaczony
                self.selected_options.pop(category, None)

    def _create_toggle_button(self):
        """Create a toggle button for collapsing/expanding options."""
        button = QPushButton("↓")
        button.setFixedSize(24, 24)
        button.setFlat(True)
        return button

    def toggle_options(self, category):
        """Toggle visibility of options for a category."""
        data = self.category_widgets[category]
        field_group = data["field_group"]
        options_widget = data["options_widget"]
        toggle_button = data["toggle_button"]

        if options_widget.isVisible():
            options_widget.setVisible(False)
            field_group.setFixedHeight(self.FIELD_HEIGHT)
            toggle_button.setText("↓")
        else:
            options_widget.setVisible(True)

            # Sprawdź, czy kategoria posiada układ siatki
            if category in self.options_layout_by_category:
                option_items = self.option_items_by_category.get(category)
                layout = self.options_layout_by_category.get(category)
                available_width = self.scroll_area.viewport().width()
                option_width = self.OPTION_WIDGET_SIZE[0]
                spacing = 10

                # Ustaw liczbę kolumn na 1 dla kategorii "Przeszklenia"
                if category == "Przeszklenia":
                    columns = 1
                else:
                    columns = max(3, available_width // (option_width + spacing))

                self._populate_grid_layout(option_items, layout, columns)

            # Calculate and adjust the height of the field group
            total_height = options_widget.sizeHint().height()
            expanded_height = self.FIELD_HEIGHT + total_height
            field_group.setFixedHeight(expanded_height)

            toggle_button.setText("↑")

    def _populate_grid_layout(self, option_items, layout, columns):
        """Populate a grid layout with option widgets."""
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                layout.removeWidget(widget)

        for index, widget in enumerate(option_items):
            row = index // columns
            column = index % columns
            layout.addWidget(widget, row, column)

    def eventFilter(self, source, event):
        """Handle resize events for dynamic updates."""
        if event.type() == QEvent.Resize:
            self._update_grid_columns()
        return super().eventFilter(source, event)

    def _update_grid_columns(self):
        """Dynamically update grid columns based on available width."""
        available_width = self.scroll_area.viewport().width()
        spacing = 10  # Margines między elementami

        for category, data in self.category_widgets.items():
            option_items = self.option_items_by_category.get(category, [])
            layout = self.options_layout_by_category.get(category)

            if not option_items or layout is None:
                continue

            # Specjalna obsługa dla kategorii "Przeszklenia"
            if category == "Przeszklenia":
                # Szerokość "Przeszklenia" jest większa (303 px)
                option_width = 303
                columns = max(1, available_width // (option_width + spacing))
            else:
                # Domyślna szerokość opcji (100 px)
                option_width = self.OPTION_WIDGET_SIZE[0]
                columns = max(1, available_width // (option_width + spacing))

            # Aktualizuj układ siatki dla opcji w tej kategorii
            self._populate_grid_layout(option_items, layout, columns)

            # Dostosuj wysokość grupy pola, jeśli opcje są widoczne
            if data["options_widget"].isVisible():
                self._adjust_field_group_height(option_items, columns, data["field_group"])

    def _populate_grid_layout(self, option_items, layout, columns):
        """Populate a grid layout with option widgets."""
        # Usuń wszystkie istniejące widgety z układu
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                layout.removeWidget(widget)

        # Dodaj widgety w nowym układzie
        for index, widget in enumerate(option_items):
            row = index // columns
            column = index % columns
            layout.addWidget(widget, row, column)

    def _adjust_field_group_height(self, option_items, columns, field_group):
        """Adjust the height of a field group based on the number of rows."""
        total_items = len(option_items)
        rows = (total_items + columns - 1) // columns  # Ceiling division
        option_height = self.OPTION_WIDGET_SIZE[1]
        spacing = 10

        new_height = max(0, rows * (option_height + spacing) - spacing + self.FIELD_HEIGHT)
        field_group.setFixedHeight(new_height)
        field_group.updateGeometry()

    def load_options_data(self, filename):
        """Load options data from a file."""
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
                elif current_gate and ': ' in line:
                    field_name, options = line.split(': ', 1)
                    options_data[current_gate][field_name] = options.split(', ')

        return options_data

    def get_selected_options(self):
        """Returns the currently selected options."""
        tmp = self.selected_options
        return tmp

    def validate_required_fields(self, required_fields):
        """Validates that all required fields from the given list have selected options."""
        all_valid = True
        for category in required_fields:
            if category == "Kolor":
                # Sprawdź, czy istnieje zaznaczony kolor w "Kolor standardowy" lub "Kolor RAL"
                kolor_standardowy_selected = "Kolor standardowy" in self.selected_options
                kolor_ral_selected = "Kolor RAL" in self.selected_options

                if not (kolor_standardowy_selected or kolor_ral_selected):
                    # Jeśli żaden kolor nie jest zaznaczony, podświetl oba pola
                    for color_category in ["Kolor standardowy", "Kolor RAL"]:
                        if color_category in self.category_widgets:
                            field_group = self.category_widgets[color_category]["field_group"]
                            field_group.setStyleSheet("QGroupBox { border: 2px solid red; border-radius: 5px; }")
                    all_valid = False
                else:
                    # Jeśli którykolwiek kolor jest zaznaczony, usuń podświetlenie z obu
                    for color_category in ["Kolor standardowy", "Kolor RAL"]:
                        if color_category in self.category_widgets:
                            field_group = self.category_widgets[color_category]["field_group"]
                            field_group.setStyleSheet("")  # Przywróć domyślny wygląd
            else:
                # Walidacja dla innych kategorii
                if category not in self.selected_options or not self.selected_options[category]:
                    # Jeśli kategoria jest niewypełniona, podświetl cały QGroupBox na czerwono
                    if category in self.category_widgets:
                        field_group = self.category_widgets[category]["field_group"]
                        field_group.setStyleSheet("QGroupBox { border: 2px solid red; border-radius: 5px; }")
                    all_valid = False
                else:
                    # Przywróć domyślny styl Qt
                    if category in self.category_widgets:
                        field_group = self.category_widgets[category]["field_group"]
                        field_group.setStyleSheet("")

        return all_valid