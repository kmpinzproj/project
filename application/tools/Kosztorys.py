import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from application.DatabaseManager import DatabaseManager
from application.path import get_resource_path


def load_json_data(file_path):
    """
    Wczytuje dane z pliku JSON.

    Args:
        file_path (str): Ścieżka do pliku JSON.

    Returns:
        dict: Słownik z danymi wczytanymi z pliku JSON.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def calculate_price(data, db_manager):
    """
    Oblicza całkowitą cenę bramy garażowej na podstawie danych wejściowych i cen z bazy danych.

    Args:
        data (dict): Dane z pliku JSON zawierające szczegóły dotyczące bramy.
        db_manager (DatabaseManager): Obiekt zarządzający połączeniem z bazą danych.

    Returns:
        tuple: Całkowita cena (int) oraz szczegóły cenowe (list).
    """
    gate_type = data.get("Typ bramy")

    try:
        width = int(data.get("Wymiary", {}).get("Szerokość", 2200))
    except (ValueError, TypeError):
        width = 2200

    try:
        height = int(data.get("Wymiary", {}).get("Wysokość", 2000))
    except (ValueError, TypeError):
        height = 2000

    price = db_manager.get_price(gate_type, 'Bazowa', 'Cena')

    price_details = []
    price_details.append(f"Cena bazowa: {gate_type} (+{price} zł)")

    for param, option in data.items():
        if param in ["Typ bramy", "Wymiary", "Nazwa projektu", "Kolor standardowy", "Kolor RAL"]:
            continue
        print(param)
        if isinstance(option, list):
            for single_option in option:
                print(single_option)
                if isinstance(single_option, (str, int, float)):
                    surcharge = db_manager.get_price(gate_type, param, str(single_option))
                    if surcharge > 0:
                        price += surcharge
                        price_details.append(f"{param}: {single_option} (+{surcharge} zł)")
        elif isinstance(option, (str, int, float)):
            surcharge = db_manager.get_price(gate_type, param, str(option))
            if surcharge > 0:
                price += surcharge
                price_details.append(f"{param}: {option} (+{surcharge} zł)")

    extra_width = max(0, width - 2200)
    extra_height = max(0, height - 2000)

    extra_width_rate = 0.5  # Cena za każdy dodatkowy mm szerokości
    extra_height_rate = 0.5 # Cena za każdy dodatkowy mm wysokości

    extra_width_cost = extra_width * extra_width_rate
    extra_height_cost = extra_height * extra_height_rate

    if extra_width > 0:
        price += extra_width_cost
        price_details.append(f"Nadmiarowa szerokość: +{extra_width} mm (+{extra_width_cost} zł)")

    if extra_height > 0:
        price += extra_height_cost
        price_details.append(f"Nadmiarowa wysokość: +{extra_height} mm (+{extra_height_cost} zł)")

    return price, price_details


class PriceCalculator(QWidget):
    """
    Widżet kalkulatora cen dla bram garażowych.

    Oblicza cenę bramy na podstawie danych z pliku JSON i wyświetla szczegóły w oknie.
    """
    def __init__(self):
        """
        Inicjalizuje widżet kalkulatora cen, wczytuje dane i wyświetla szczegóły kalkulacji.
        """
        super().__init__()
        self.setWindowTitle("Kalkulator Cen Bramy Garażowej")
        self.setGeometry(100, 100, 400, 500)
        layout = QVBoxLayout()

        db_manager = DatabaseManager()

        data = load_json_data(get_resource_path('resources/selected_options.json'))
        total_price, price_details = calculate_price(data, db_manager)

        summary = "Parametry:\n"
        for detail in price_details:
            summary += f"  - {detail}\n"
        summary += f"\nCena całkowita: {total_price} zł"

        label = QLabel(summary)
        layout.addWidget(label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    calculator = PriceCalculator()
    calculator.show()
    app.exec()
