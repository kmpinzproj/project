import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from Okno_startowe import OknoStartowe
from Okno_wymiarów import OknoWymiarow
from Wybór_bramy import WyborBramy
from Kreator import Kreator
from Formularz_kontaktowy import ContactForm

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")

        # Initialize QStackedWidget and set it as central widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize views
        self.start_view = OknoStartowe()
        self.dimension_view = OknoWymiarow()
        self.gate_selection_view = WyborBramy()
        self.gate_creator_view = Kreator()
        self.connect_form_view = ContactForm()

        # Add views to stack
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.dimension_view)
        self.stack.addWidget(self.gate_selection_view)
        self.stack.addWidget(self.gate_creator_view)
        self.stack.addWidget(self.connect_form_view)

        # Connect button in start view to switch view
        self.start_view.create_new_button.clicked.connect(self.show_gate_selection_view)

        # Connect button in gate selection view to switch view
        self.gate_selection_view.back_button.clicked.connect(self.back_to_start_view)
        self.gate_selection_view.accept_button.clicked.connect(self.show_dimension_view)

        # Connect button in dimension view to switch view
        self.dimension_view.back_button.clicked.connect(self.back_to_gate_selection_view)
        self.dimension_view.accept_button.clicked.connect(self.show_gate_creator)

        # Connect button in gate selection view to switch view
        self.gate_creator_view.back_button.clicked.connect(self.back_to_dimension_view)
        self.gate_creator_view.save_button.clicked.connect(self.show_contact_form_view)

        # Connect button in contact form view to switch view
        self.connect_form_view.back_button.clicked.connect(self.back_to_gate_creator)
        self.connect_form_view.submit_button.clicked.connect(self.back_to_start_view)


    def show_dimension_view(self):
        self.stack.setCurrentWidget(self.dimension_view)

    def show_gate_selection_view(self):
        self.stack.setCurrentWidget(self.gate_selection_view)

    def show_gate_creator(self):
        self.stack.setCurrentWidget(self.gate_creator_view)

    def show_contact_form_view(self):
        self.stack.setCurrentWidget(self.connect_form_view)

    def back_to_start_view(self):
        self.stack.setCurrentWidget(self.start_view)

    def back_to_dimension_view(self):
        self.stack.setCurrentWidget(self.dimension_view)

    def back_to_gate_selection_view(self):
        self.stack.setCurrentWidget(self.gate_selection_view)

    def back_to_gate_creator(self):
        self.stack.setCurrentWidget(self.gate_creator_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec())