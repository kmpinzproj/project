import trimesh
import numpy as np
import matplotlib.pyplot as plt


def is_diagonal(v0, v1):
    """
    Sprawdza, czy krawędź jest ukośna.
    W tym przypadku linia ukośna ma podobną długość w osiach X i Y.
    """
    vec = v1 - v0
    return not (np.isclose(vec[0], 0) or np.isclose(vec[1], 0))

def draw_non_diagonal_edges(obj_file_path, output_image_path):
    # Wczytaj plik OBJ
    mesh = trimesh.load(obj_file_path)

    # Wyciągnij wszystkie krawędzie i wierzchołki
    edges = mesh.edges
    vertices = mesh.vertices

    # Rysowanie tylko krawędzi nieukośnych
    plt.figure(figsize=(10, 10))
    for edge in edges:
        v0, v1 = vertices[edge[0]], vertices[edge[1]]
        if not is_diagonal(v0, v1):
            plt.plot([v0[0], v1[0]], [v0[1], v1[1]], color='black', linewidth=0.5)

    # Ustawienia osi i proporcji
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(output_image_path, dpi=300)

# Ścieżka do pliku .obj i zapis wyjściowego obrazu
input_obj_file = "../generator/model.obj"
output_image_file = "../generator/sketch_final.png"

# Rysowanie szkicu
draw_non_diagonal_edges(input_obj_file, output_image_file)