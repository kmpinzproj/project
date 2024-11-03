from PySide6.QtWidgets import (QMainWindow,QSpacerItem,QSizePolicy, QWidget,
                               QPushButton, QListWidget,QSplitter, QVBoxLayout,
                               QHBoxLayout, QStyleFactory)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from Rozwijane_menu import ScrollableMenu
from button import StyledButton

class Kreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 800, 600)

        # Central widget setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)

        # Spacer to push content to vertical center
        # left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        menu = ScrollableMenu()
        left_layout.addWidget(menu)

        # Spacer to keep the input fields centered, buttons remain at the bottom
        # left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add left widget to splitter
        main_layout.addWidget(left_widget)

        # Right side layout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Right section with 3D view
        openGLWidget = QOpenGLWidget()
        openGLWidget.setObjectName(u"openGLWidget")

        # Button section
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.back_button = StyledButton("Cofnij")
        self.save_button = StyledButton("Zapisz")

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.save_button)

        right_layout.addWidget(openGLWidget)
        right_layout.addWidget(buttons_widget)
        main_layout.addWidget(right_widget)

        # Adding layouts to main layout
        main_layout.addWidget(right_widget)

        m = QVBoxLayout(central_widget)
        m.addWidget(main_widget)



