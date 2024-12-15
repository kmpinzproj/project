import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tkinter import Tk, filedialog

# Register a font that supports Polish characters
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))


def create_pdf():
    # Load JSON data from file
    json_path = "../resources/selected_options.json"

    if not os.path.exists(json_path):
        print(f"Error: JSON file '{json_path}' not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract dimensions from the data if available
    dimensions = None
    if 'Wymiary' in data and isinstance(data['Wymiary'], dict):
        width = data['Wymiary'].get('Szerokość')
        height = data['Wymiary'].get('Wysokość')
        if width and height:
            dimensions = f"{width} x {height}"

    # Prompt the user to choose the save location for the PDF
    root = Tk()
    root.withdraw()  # Hide the root window
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not output_path:
        print("No file selected for saving the PDF.")
        return

    # Remove the existing file if it exists
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except PermissionError as e:
            print(f"Error: Unable to delete the existing PDF file. {e}")
            return

    pdf = SimpleDocTemplate(output_path, pagesize=A4, topMargin=0, bottomMargin=0)

    # Create a list to hold PDF elements
    elements = []

    # Add images one below the other
    image_paths = ["../generator/image_with_arrows.png", "../generator/sketch_iso_no_diagonals.png"]

    page_width, page_height = A4
    image_width = page_width  # Full width
    image_height = image_width * 0.5  # Maintain aspect ratio for images

    for image_path in image_paths:
        if os.path.exists(image_path):
            image = Image(image_path, width=image_width, height=image_height)  # Resize image
            elements.append(image)
        else:
            print(f"Warning: Image '{image_path}' not found.")

    # Create the vertical table from JSON data
    if isinstance(data, dict) and data:
        # Prepare the table data as key-value pairs
        formatted_table_data = []
        for key, value in data.items():
            if key == 'Wymiary' and dimensions:
                formatted_table_data.append(["Wymiary", dimensions])
            else:
                if isinstance(value, list):
                    value = ", ".join(map(str, value))  # Convert list to comma-separated string
                formatted_table_data.append([key, str(value)])

        # Create vertical table
        table = Table(formatted_table_data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    else:
        print("Warning: No valid data found in JSON.")

    # Build the PDF
    pdf.build(elements)
    print(f"PDF successfully created at '{os.path.abspath(output_path)}'")