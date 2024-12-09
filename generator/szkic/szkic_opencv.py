import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def detect_and_draw_arrows(image_path, output_path):
    """
    Wykrywa kontury na obrazie i rysuje strzałki pokazujące szerokość i wysokość obiektu.
    """
    print("Wykrywanie krawędzi i rysowanie strzałek...")
    image = Image.open(image_path)
    image_cv = np.array(image.convert('L'))
    edges = cv2.Canny(image_cv, threshold1=50, threshold2=150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("Nie wykryto żadnych konturów w obrazie.")

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    left_edge, right_edge, top_edge, bottom_edge = x, x + w, y, y + h

    print(
        f"Znaleziono obiekt o współrzędnych: Left={left_edge}, Right={right_edge}, Top={top_edge}, Bottom={bottom_edge}")
    print(f"Szerokość obiektu: {w}px, Wysokość obiektu: {h}px")

    bottom_width_arrow_image = image.copy()
    draw = ImageDraw.Draw(bottom_width_arrow_image)

    # Ustawienie ścieżki do czcionki obsługującej polskie znaki
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux
        # font_path = "C:/Windows/Fonts/arial.ttf"  # Windows (zależnie od systemu)
        font = ImageFont.truetype(font_path, 80)  # Rozmiar czcionki
    except IOError:
        print("Nie znaleziono czcionki. Używana jest czcionka domyślna (bez polskich znaków).")
        font = ImageFont.load_default()

    # Rysowanie strzałki szerokości
    width_arrow_start_bottom = (left_edge, bottom_edge + 40)
    width_arrow_end_bottom = (right_edge, bottom_edge + 40)
    draw_arrow(draw, width_arrow_start_bottom, width_arrow_end_bottom, direction='horizontal')
    draw.text(((left_edge + right_edge) / 2 - 150, bottom_edge + 50),
              f"Szerokosc: {w} px", fill="black", font_size=50)

    # Rysowanie strzałki wysokości
    height_arrow_start_left = (left_edge - 40, top_edge)
    height_arrow_end_left = (left_edge - 40, bottom_edge)
    draw_arrow(draw, height_arrow_start_left, height_arrow_end_left, direction='vertical')
    draw.text((left_edge - 450, (top_edge + bottom_edge) / 2 - 40),  # Przesunięcie w lewo
              f"Wysokosc: {h} px", fill="black", font_size=50)

    bottom_width_arrow_image.save(output_path)
    print(f"Obraz ze strzałkami zapisany jako: {output_path}")
    return output_path


def draw_arrow(draw, start, end, direction='horizontal'):
    """
    Rysuje strzałkę na podanym obrazie.
    """
    draw.line([start, end], fill="black", width=3)
    if direction == 'horizontal':
        draw.polygon([(start[0] + 10, start[1] - 5), (start[0] + 10, start[1] + 5), (start[0], start[1])], fill="black")
        draw.polygon([(end[0] - 10, end[1] - 5), (end[0] - 10, end[1] + 5), (end[0], end[1])], fill="black")
    elif direction == 'vertical':
        draw.polygon([(start[0] - 5, start[1] + 10), (start[0] + 5, start[1] + 10), (start[0], start[1])], fill="black")
        draw.polygon([(end[0] - 5, end[1] - 10), (end[0] + 5, end[1] - 10), (end[0], end[1])], fill="black")


def main():
    """
    Główna funkcja rysująca strzałki na obrazie.
    """
    image_path = '../generator/sketch_final.png'
    final_output_path = '../generator/image_with_arrows.png'

    try:
        # Wykryj wymiary i narysuj strzałki
        detect_and_draw_arrows(image_path, final_output_path)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    main()