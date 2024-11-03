from PySide6.QtCore import QCoreApplication, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QMainWindow, QWidget, QFormLayout, QFrame,
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGraphicsView, QMenuBar, QStatusBar)
from button import StyledButton

class WyborBramy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main layout setup
        main_layout = QVBoxLayout(central_widget)

        # Form layout setup
        self.form_layout = QFormLayout()
        main_layout.addLayout(self.form_layout)

        # Create frames and their layouts
        self.create_frame_1()
        self.create_frame_2()
        self.create_frame_3()
        self.create_frame_4()

        # Button section
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        # Add the button at the bottom
        self.back_button = StyledButton("Cofnij")
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        self.accept_button = StyledButton("Akceptuj")
        buttons_layout.addWidget(self.accept_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(buttons_widget)
        # Menu and status bar setup
        # self.menubar = QMenuBar(self)
        # self.setMenuBar(self.menubar)
        # self.statusbar = QStatusBar(self)
        # self.setStatusBar(self.statusbar)

    def create_frame_1(self):
        frame = self.create_inner_frame("Brama Rozwierana",
                                         "Nie wymagają wolnego miejsca wewnątrz garażu oraz wolnego naproża. Można zamontować je praktycznie w każdym garażu. Ekonomiczne rozwiązanie za rozsądną cenę.")
        self.form_layout.setWidget(0,QFormLayout.LabelRole, frame)

    def create_frame_2(self):
        frame = self.create_inner_frame("Brama Roletowa",
                                         "Odpowiednie rozwiązanie dla osób, które cenią funkcjonalność. Oszczędność miejsca w garażu i na podjeździe, a zarazem napęd elektryczny w standardzie.")
        self.form_layout.setWidget(0, QFormLayout.FieldRole, frame)

    def create_frame_3(self):
        frame = self.create_inner_frame("Brama Uchylna",
                                         "Prostota, tradycja i nowoczesność. Najczęściej stosowane w nieocieplonych garażach wolnostojących lub w budynkach wielomieszkaniowych.")
        self.form_layout.setWidget(1, QFormLayout.LabelRole, frame)

    def create_frame_4(self):
        frame = self.create_inner_frame("Brama Segmentowa",
                                         "Najbardziej komfortowe rozwiązanie do garażu. Otwierane pionowo w górę oszczędzają miejsce przed i wewnątrz garażu. Ciepłe i ciche połączenie do garaży ogrzewanych.")
        self.form_layout.setWidget(1, QFormLayout.FieldRole, frame)

    def create_inner_frame(self, title, description):
        frame = QFrame()
        frame.setMinimumSize(QSize(401, 231))
        frame.setMaximumSize(QSize(401, 231))
        frame.setStyleSheet("background-color: rgb(255, 249, 218);")
        vertical_layout = QVBoxLayout(frame)

        label_title = QLabel(title)
        font = QFont()
        font.setBold(True)
        label_title.setFont(font)
        label_title.setStyleSheet("color: rgb(105, 64, 14);")
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vertical_layout.addWidget(label_title)

        label_description = QLabel(description)
        label_description.setStyleSheet("color: rgb(74,68,61);")
        label_description.setWordWrap(True)
        vertical_layout.addWidget(label_description)

        frame_inner = QFrame(frame)
        horizontal_layout = QHBoxLayout(frame_inner)

        graphics_view = QGraphicsView(frame_inner)
        horizontal_layout.addWidget(graphics_view)

        button = QPushButton("Wybierz", frame_inner)
        horizontal_layout.addWidget(button)

        vertical_layout.addWidget(frame_inner)
        return frame

    def add_back_button(self, layout):
        self.back_button = QPushButton("Cofnij", self)
        self.back_button.setFixedHeight(30)  # Set a minimum size for the button
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)