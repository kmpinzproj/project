from PySide6.QtWidgets import (QMainWindow,QSpacerItem,QSizePolicy, QWidget,
                               QPushButton, QListWidget,QSplitter, QVBoxLayout,
                               QHBoxLayout, QStyleFactory)
from PySide6.QtCore import Qt
from button import StyledButton

class OknoStartowe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 800, 600)

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        g_widget = QWidget()
        g_layout = QHBoxLayout(g_widget)
        # Left section with buttons
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)

        # Spacer to push content to vertical center
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Button for create and open project
        self.create_new_button = StyledButton("Stwórz nowy")
        self.open_saved_button = StyledButton("Otwórz zapisany")
        left_layout.addWidget(self.create_new_button)
        left_layout.addWidget(self.open_saved_button)

        # Spacer to keep the input fields centered, buttons remain at the bottom
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add left widget to splitter
        g_layout.addWidget(left_widget)

        # Right side layout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Right section with project list
        project_list = QListWidget()
        project_list.addItem("Lista zapisanych projektów")
        right_layout.addWidget(project_list)

        # Adding layouts to main layout
        g_layout.addWidget(right_widget)

        # Setting the main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(g_widget)
