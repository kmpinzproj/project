from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QGroupBox, QPushButton, QCheckBox, \
    QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class ScrollableMenu(QWidget):
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
            # Grupa reprezentująca każde pole
            field_group = QGroupBox()
            field_layout = QVBoxLayout(field_group)
            field_group.setFixedHeight(100)  # Ustawienie początkowej stałej wysokości pola

            # Nagłówek pola
            header_layout = QHBoxLayout()
            label = QLabel(field_name)
            label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            header_layout.addWidget(label)

            # Przycisk z symbolem strzałki
            toggle_button = QPushButton("↓")  # Strzałka w dół na start
            toggle_button.setFixedSize(24, 24)
            toggle_button.setFlat(True)

            # Dodaj nagłówek do layoutu
            field_layout.addLayout(header_layout)  # Nagłówek na górze

            # Stworzenie ukrytego widżetu opcji
            options_widget = QWidget()
            options_layout = QVBoxLayout(options_widget)
            options_widget.setVisible(False)  # Początkowo ukryty

            # Dodawanie CheckBox'ów jako opcje wyboru
            for option in options:
                checkbox = QCheckBox(option)
                options_layout.addWidget(checkbox)

            # Dodaj ukryty widget opcji do layoutu
            field_layout.addWidget(options_widget)

            # Połączenie przycisku z funkcją toggle, przekazując widżet opcji i przycisk
            toggle_button.clicked.connect(lambda checked, opt_widget=options_widget, field_grp=field_group,
                                                 btn=toggle_button: self.toggle_options(field_grp, opt_widget, btn))
            header_layout.addWidget(toggle_button, alignment=Qt.AlignRight)

            content_layout.addWidget(field_group)

            # Ustaw layout opcji w ukrytym widgetcie
            options_widget.setLayout(options_layout)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

    def toggle_options(self, field_group, options_widget, toggle_button):
        # Przełącz widoczność opcji i dostosuj wysokość pola
        if options_widget.isVisible():
            options_widget.setVisible(False)
            field_group.setFixedHeight(100)  # Powrót do początkowej wysokości
            toggle_button.setText("↓")  # Zmień tekst na strzałkę w dół
        else:
            options_widget.setVisible(True)
            expanded_height = 100 + options_widget.sizeHint().height()  # Wysokość po rozwinięciu
            field_group.setFixedHeight(expanded_height)
            toggle_button.setText("↑")  # Zmień tekst na strzałkę w górę


