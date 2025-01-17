from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QFrame, QVBoxLayout,
    QHBoxLayout, QLabel, QSizePolicy
)

from application.tools.button import StyledButton
import os
import json


class WyborBramy(QMainWindow):
    """
    Klasa reprezentująca widok wyboru typu bramy w aplikacji.

    Pozwala użytkownikowi wybrać typ bramy, wyświetlając dostępne opcje w formie
    ramek z opisem, zdjęciem oraz przyciskiem wyboru.
    """
    # Constants for frame size
    FRAME_WIDTH = 390
    FRAME_HEIGHT = 220

    def __init__(self, dimension_view):
        """
        Inicjalizuje widok wyboru bramy.

        Args:
            dimension_view (function): Funkcja przechodząca do widoku wymiarów.
        """
        super().__init__()
        self.back_button = None
        self.accept_button = None
        self.dimension_view = dimension_view
        self.pixmap_cache = {}  # Cache dla oryginalnych pixmap
        self.setWindowTitle("Wybór bramy")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Zachowanie minimalnego rozmiaru

        # Central widget setup
        central_widget = QWidget(self)
        central_widget.setObjectName("wyborBramyWindow")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Grid layout for frames
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        # Frames setup with dictionary for easier updates
        gates = {
            "Brama Rozwierana": "Nie wymagają wolnego miejsca wewnątrz garażu oraz wolego naproża. Można zamontować je praktycznie w każdym garażu. Ekonomiczne rozwiązanie za rozsądną cenę.",
            "Brama Roletowa": "Odpowiednie rozwiązanie dla osób, które cenią funkcjonalność. Oszczędność miejsca w garażu i na podjeździe, a zarazem napęd elektryczny w standardzie.",
            "Brama Uchylna": "Prostota , tradycja i nowoczesność. Najczęściej stosowane w nieocieplonych garażach wolnostojących lub w budynkach wielomieszkaniowych.",
            "Brama Segmentowa": "Najbardziej komfortowe rozwiązanie do garażu. Otwierane pionowo w górę oszczędzają miejsce przed i wewnątrz garażu. Ciepłe i ciche polecane do garaży ogrzewanych."
        }

        # Dynamically add frames from the gates dictionary
        for index, (title, description) in enumerate(gates.items()):
            row, column = divmod(index, 2)  # Determine row and column
            self.add_frame(title, description, row, column)

        # Button section
        self.setup_buttons(main_layout)

        # Rozciąganie grid layout
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 0)

    def add_frame(self, title, description, row, column):
        """
        Dodaje ramkę z podanym tytułem i opisem do siatki w określonym wierszu i kolumnie.

        Args:
            title (str): Tytuł ramki (np. nazwa bramy).
            description (str): Opis bramy.
            row (int): Wiersz w układzie siatki.
            column (int): Kolumna w układzie siatki.
        """
        frame = self.create_inner_frame(title, description)
        self.grid_layout.addWidget(frame, row, column)

    def create_inner_frame(self, title, description):
        """
        Tworzy ramkę dla danego typu bramy, zawierającą tytuł, opis, obraz oraz przycisk wyboru.

        Args:
            title (str): Tytuł ramki (np. nazwa bramy).
            description (str): Opis bramy.

        Returns:
            QFrame: Ramka z widżetami opisującymi typ bramy.
        """
        frame = QFrame()
        frame.setObjectName("gateFrame")
        frame.setMinimumSize(QSize(self.FRAME_WIDTH, self.FRAME_HEIGHT))

        vertical_layout = QVBoxLayout(frame)
        vertical_layout.setContentsMargins(5, 5, 5, 5)  # Marginesy ramki
        vertical_layout.setSpacing(5)  # Odstępy między elementami

        # Title setup
        label_title = self.create_title_label(title)
        vertical_layout.addWidget(label_title)

        # Description setup
        label_description = self.create_description_label(description)
        vertical_layout.addWidget(label_description)

        # Image setup
        image_path = os.path.abspath(f"../jpg/Brama/{title}.png")
        self.label_image = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.label_image.setPixmap(pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.label_image.setPixmap(QPixmap(350, 250))  # Placeholder pixmap in case of missing file
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_image.setObjectName("image_label")  # Unikalny identyfikator QLabel
        self.label_image._original_pixmap = QPixmap(image_path).scaled(250, 150, Qt.KeepAspectRatio,
                                                                       Qt.SmoothTransformation)
        self.label_image.setPixmap(self.label_image._original_pixmap)
        # Inner frame with image and selection button
        frame_inner = QFrame(frame)
        horizontal_layout = QHBoxLayout(frame_inner)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)

        # Adding image
        horizontal_layout.addWidget(self.label_image, alignment=Qt.AlignLeft)

        # Adding button
        button = StyledButton("Wybierz", frame_inner)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.clicked.connect(lambda _, g=title: (self.dimension_view(), self.save_gate_type(g)))
        horizontal_layout.addWidget(button, alignment=Qt.AlignRight)

        vertical_layout.addWidget(frame_inner)
        return frame

    def create_title_label(self, title):
        """
        Tworzy etykietę tytułu dla ramki.

        Args:
            title (str): Tytuł do wyświetlenia.

        Returns:
            QLabel: Etykieta z tytułem.
        """
        label_title = QLabel(title)
        label_title.setObjectName("gateTitleLabel")  # Identyfikator
        font = QFont()
        font.setBold(True)
        label_title.setFont(font)
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label_title

    def create_description_label(self, description):
        """
        Tworzy etykietę opisu dla ramki.

        Args:
            description (str): Opis do wyświetlenia.

        Returns:
            QLabel: Etykieta z opisem.
        """
        label_description = QLabel(description)
        label_description.setObjectName("gateDescriptionLabel")  # Identyfikator
        label_description.setWordWrap(True)
        return label_description

    def setup_buttons(self, layout):
        """
        Konfiguruje przyciski nawigacyjne na dole widoku.

        Args:
            layout (QVBoxLayout): Główny układ widoku, do którego zostaną dodane przyciski.
        """
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.back_button = StyledButton("Cofnij")

        # Add buttons with centered alignment
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(buttons_widget)
        buttons_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def resizeEvent(self, event):
        """
        Obsługuje zdarzenie zmiany rozmiaru okna, dynamicznie dostosowując rozmiar obrazów w ramkach.

        Args:
            event (QResizeEvent): Zdarzenie zmiany rozmiaru.
        """
        super().resizeEvent(event)

        # Oblicz szerokość ramki (w zależności od rozmiaru okna)
        available_width = self.size().width() - 40  # Szerokość okna - marginesy
        column_count = 2  # Liczba kolumn w układzie siatki
        frame_width = (available_width // column_count) - 20  # Szerokość ramki z marginesem
        image_width = int(frame_width * 0.9)  # Zdjęcie zajmuje 90% szerokości ramki
        image_height = int(image_width * 0.6)  # Zachowanie proporcji zdjęcia (3:2)

        # Iteruj przez wszystkie ramki w układzie siatki
        for i in range(self.grid_layout.count()):
            frame = self.grid_layout.itemAt(i).widget()
            if frame:
                label_image = frame.findChild(QLabel, "image_label")
                if label_image:
                    original_pixmap = getattr(label_image, "_original_pixmap", None)
                    if original_pixmap is None:
                        # Przechowuj oryginalny pixmap przy pierwszym wywołaniu
                        label_image._original_pixmap = label_image.pixmap()

                    pixmap = label_image._original_pixmap
                    if pixmap:
                        label_image.setPixmap(
                            pixmap.scaled(image_width, image_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        )

    @staticmethod
    def save_gate_type(gate_type):
        """
        Zapisuje wybrany typ bramy do pliku JSON.

        Args:
            gate_type (str): Wybrany typ bramy do zapisania.
        """
        file_path = "../resources/selected_options.json"
        try:
            # Sprawdź, czy plik istnieje; jeśli nie, utwórz go z pustym słownikiem
            if not os.path.isfile(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump({}, file, ensure_ascii=False, indent=4)

            # Załaduj istniejące dane z pliku
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Zapisz typ bramy
            data["Typ bramy"] = gate_type

            # Zapisz zaktualizowane dane do pliku
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as e:
            print(f"Wystąpił błąd podczas operacji na pliku: {e}")
        except Exception as e:
            print(f"Wystąpił niespodziewany błąd: {e}")