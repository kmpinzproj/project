import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from DatabaseManager import DatabaseManager

def load_json_data(file_path):
    """Wczytaj dane z pliku JSON."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def calculate_price(data, db_manager):
    gate_type = data.get("Typ bramy")

    try:
        width = int(data.get("Wymiary", {}).get("Szerokość", 2500))
    except (ValueError, TypeError):
        width = 2500

    try:
        height = int(data.get("Wymiary", {}).get("Wysokość", 2125))
    except (ValueError, TypeError):
        height = 2125

    price = db_manager.get_price(gate_type, 'Bazowa', 'Cena')

    price_details = []

    for param, option in data.items():
        if param in ["Typ bramy", "Wymiary", "Nazwa projektu"]:
            continue

        if isinstance(option, list):
            for single_option in option:
                if isinstance(single_option, (str, int, float)):
                    surcharge = db_manager.get_price(gate_type, param, str(single_option))
                    price += surcharge
                    price_details.append(f"{param}: {single_option} (+{surcharge} zł)")
        elif isinstance(option, (str, int, float)):
            surcharge = db_manager.get_price(gate_type, param, str(option))
            price += surcharge
            price_details.append(f"{param}: {option} (+{surcharge} zł)")

    extra_width = max(0, width - 2500)
    extra_height = max(0, height - 2125)

    extra_width_rate = 1  # Cena za każdy dodatkowy mm szerokości
    extra_height_rate = 1  # Cena za każdy dodatkowy mm wysokości

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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalkulator Cen Bramy Garażowej")
        self.setGeometry(100, 100, 400, 500)
        layout = QVBoxLayout()

        db_manager = DatabaseManager()

        data = load_json_data('../resources/selected_options.json')
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
